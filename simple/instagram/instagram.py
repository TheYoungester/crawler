# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 23:22:19 2018

@author: Administrator
"""

import hashlib
import json
import random
import re
import time

import requests
from pyquery import PyQuery as pq
import urllib
import urllib.parse
import os
import pymysql
# mysql connection
conn = pymysql.connect("39.105.207.51", "root", "123456", "crawler")
cursor = conn.cursor()
# tags which to search
tags = ['手账', '手掌', '收账', '手帳', 'bulletjournal', 'bulletjournals', 'brushinglettering']
# base query url
uri_ins = 'https://www.instagram.com/explore/tags/{0}/?__a=1'
uri_next_page = 'https://www.instagram.com/graphql/query/?query_hash=174a5243287c5f3a7de741089750ab3b&variables={0}'

# 图片详情 https://www.instagram.com/graphql/query/?query_hash=fead941d698dc1160a298ba7bec277ac&variables=%7B%22shortcode%22%3A%22B1icOBshkkN%22%2C%22child_comment_count%22%3A3%2C%22fetch_comment_count%22%3A40%2C%22parent_comment_count%22%3A24%2C%22has_threaded_comments%22%3Atrue%7D
# the dir to save download images
baseDir = 'C:/Users/Administrator/Desktop/crawler/ins'
headers = {
    'Connection': 'keep-alive',
    'Host': 'www.instagram.com',
    'Referer': 'https://www.instagram.com/instagram/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

proxy = {
}


def hashStr(strInfo):
    h = hashlib.md5()
    h.update(strInfo.encode("utf-8"))
    return h.hexdigest()


def get_html(url):
    try:
        response = requests.get(url, headers=headers, proxies=proxy)
        if response.status_code == 200:
            return response.text
        else:
            print('请求网页源代码错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_json(headers, url):
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print('请求网页json错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(headers, url)


def parseResourceJson(resourceJson, tag_name):
    imageLists = []
    data = json.loads(resourceJson, strict=False)
    hashtag = data['graphql']['hashtag']
    print(hashtag)
    id = hashtag['id']
    name = hashtag['name']
    allow_following = 1 if hashtag['allow_following'] else 0
    is_following = 1 if hashtag['is_following'] else 0
    is_top_media_only = 1 if hashtag['is_top_media_only'] else 0
    profile_pic_url = hashtag['profile_pic_url']
    count = hashtag['edge_hashtag_to_media']['count']
    sql = "INSERT INTO `crawler`.`hashtag`(`id`, `name`, `allow_following`, `is_following`, `is_top_media_only`, `profile_pic_url`, `count`) VALUES ('%s', '%s', %s, %s, %s, '%s', %s)" %(id, name, allow_following, is_following, is_top_media_only, profile_pic_url, count)
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        conn.rollback()
    handleResultData(hashtag, imageLists, tag_name)
    return downloadImages(imageLists)


def handleResultData(hashtag, imageLists, tag_name):
    hashId = hashtag['id']
    name = hashtag['name']
    edgeHashtagToMedia = hashtag['edge_hashtag_to_media']
    count = edgeHashtagToMedia['count']
    edges = edgeHashtagToMedia['edges']
    pageInfo = edgeHashtagToMedia['page_info']
    hasNextPage = pageInfo['has_next_page']  # 是否有下一页
    endCursor = pageInfo['end_cursor']
    for edge in edges:
        id = edge['node']['id']
        if len(edge['node']['edge_media_to_caption']['edges']) > 0:
            edgeMediaToCaption = edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
        else:
            edgeMediaToCaption = ''
        shortcode = edge['node']['shortcode']
        edgeMediaToComment = edge['node']['edge_media_to_comment']['count']
        takenAtTimestamp = edge['node']['taken_at_timestamp']
        height = edge['node']['dimensions']['height']
        width = edge['node']['dimensions']['width']
        displayUrl = edge['node']['display_url']
        edgeLikedBy = edge['node']['edge_liked_by']['count']
        edgeMediaPreviewLike = edge['node']['edge_media_preview_like']['count']
        owner = edge['node']['owner']['id']
        thumbnailSrc = edge['node']['thumbnail_src']
        isVideo = 1 if edge['node']['is_video'] else 0
        if hasattr(edge, 'accessibility_caption'):
            accessibilityCaption = edge['node']['accessibility_caption']
        else:
            accessibilityCaption= ''
        imageName = hashId + '-' + id
        imageLists.append({'id': id,
                           'hashId': hashId,
                           'tagName': tag_name,
                           'imageName': imageName,
                           'edgeMediaToCaption': edgeMediaToCaption,
                           'shortcode': shortcode,
                           'edgeMediaToComment': edgeMediaToComment,
                           'takenAtTimestamp': takenAtTimestamp,
                           'height': height,
                           'width': width,
                           'displayUrl': displayUrl,
                           'edgeLikedBy': edgeLikedBy,
                           'edgeMediaPreviewLike': edgeMediaPreviewLike,
                           'owner': owner,
                           'thumbnailSrc': thumbnailSrc,
                           'isVideo': isVideo,
                           'accessibilityCaption': accessibilityCaption})
    print(len(imageLists))
    if hasNextPage:
        variables = {"tag_name": tag_name,
                     "first": 300,
                     "after": endCursor}
        print(endCursor)
        url_next_page = uri_next_page.format(urllib.parse.quote(json.dumps(variables)))
        result = json.loads(get_html(url_next_page), strict=False)
        hashtag = result['data']['hashtag']
        handleResultData(hashtag, imageLists, tag_name) # 递归获取分页数据
    else:
        print(tag_name + '-总计：')
        print(len(imageLists))

def downloadImages(imageList):
    for image in imageList:
        try:
            sql_max_id = 'SELECT MAX(id) FROM `edge_hashtag_to_media`'
            cursor.execute(sql_max_id)
            results = cursor.fetchall()
            imagename = results[0][0]
            tagname = image['tagName']
            displayUrl = image['displayUrl']
            path = baseDir + '/' + tagname
            r = requests.get(displayUrl, timeout=3000)
            r.encoding = r.apparent_encoding
            if not os.path.exists(path):
                os.makedirs(path)  # create tag file dir
            with open(path + '/' + str(imagename) + '.jpg', 'wb') as f:
                f.write(r.content)
                f.close()
                print('tag: ' + tagname + '[' + str(imagename) + 'load success]')
            sql = "INSERT INTO `crawler`.`edge_hashtag_to_media`(`hashtag_id`, `tag_name`," \
                  " `image_name`, `edge_media_to_caption`, `shortcode`, `edge_media_to_comment`," \
                  " `taken_at_timestamp`, `height`, `width`, `display_url`, `edge_liked_by`, " \
                  "`edge_media_preview_like`, `owner`, `thumbnail_src`, `is_video`, " \
                  "`accessibility_caption`, `success`) VALUES " \
                  "('%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, '%s', %s, %s, '%s', '%s', %s, '%s', %s)" % \
                  (image['hashId'], image['tagName'], image['imageName'], image['edgeMediaToCaption'],
                   image['shortcode'], image['edgeMediaToComment'], image['takenAtTimestamp'],
                   image['height'], image['width'], image['displayUrl'], image['edgeLikedBy'],
                   image['edgeMediaPreviewLike'], image['owner'], image['thumbnailSrc'],
                   image['isVideo'], image['accessibilityCaption'], 0)

            cursor.execute(sql)
            conn.commit()
        except:
            print('tag: ' + tagname + '[' + str(imagename) + 'load failed]')
            print(sql)
            continue

def main():
    # read config form table config
    nextpage = 'variables=%7B%22tag_name%22%3A%22%E6%89%8B%E8%B4%A6%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFCS3RDTVppbjBaM2VGUzdCTWtnNGU2YTlLb2JTQk5KdTZfVGFSUHNZS3lxemtJM3lERjRRX0lLLV9meWZGVWxwc2dFQmhTRkYtbW4yWUc3eHFNX25UdQ%3D%3D%22%7D'
    print(urllib.parse.unquote(nextpage))
    cursor.execute('SELECT tag FROM config WHERE type=1;')
    results = cursor.fetchall()
    for row in results:
        item = row[0]
        print(urllib.parse.quote(item))
        url = uri_ins.format(urllib.parse.quote(item))
        print(get_html(url))
        resourceJson = get_html(url)
        parseResourceJson(resourceJson, item)



if __name__ == '__main__':
    start = time.time()
    main()
