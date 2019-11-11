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


def parseResourceJson(resourceJson):
    imageLists = []
    data = json.loads(resourceJson)
    id = data['graphql']['hashtag']['id']
    name = data['graphql']['hashtag']['name']
    edge_hashtag_to_media = data['graphql']['hashtag']['edge_hashtag_to_media']
    count = edge_hashtag_to_media['count']
    edges = edge_hashtag_to_media['edges']
    for edge in edges:
        eddgeId = edge['node']['id']
        edge_media_to_caption = edge['node']['edge_media_to_caption']
        edge_media_to_comment = edge['node']['edge_media_to_comment']
        display_url = edge['node']['display_url']
        edge_liked_by = edge['node']['edge_liked_by']
        edge_media_preview_like = edge['node']['edge_media_preview_like']
        thumbnail_src = edge['node']['thumbnail_src']
        is_video = edge['node']['is_video']
        # accessibility_caption = edge['node']['accessibility_caption']
        imageName = str(id) + '#' + str(eddgeId) + '#' + str(edge_liked_by['count']) + '#' + str(
            edge_hashtag_to_media['count'])  # 图片名称
        imageLists.append({'tagName': name, 'display_url': display_url, 'imageName': imageName})
        # insert into mysql
        cursor.execute()

    return downloadImages(imageLists)


def downloadImages(imageList):
    for image in imageList:
        try:
            tagname = image['tagName']
            display_url = image['display_url']
            imagename = image['imageName']
            path = baseDir + '/' + tagname
            r = requests.get(display_url, timeout=3000)
            r.encoding = r.apparent_encoding
            if not os.path.exists(path):
                os.makedirs(path)  # create tag file dir
            with open(path + '/' + imagename + '.jpg', 'wb') as f:
                f.write(r.content)
                f.close()
                print('tag: ' + tagname + '[' + imagename + 'load success]')
        except:
            print('tag: ' + tagname + '[' + imagename + 'load failed]')
            continue


def main():
    for item in tags:
        print(urllib.parse.quote(item))
        url = uri_ins.format(urllib.parse.quote(item))
        print(get_html(url))
        resourceJson = get_html(url)
        parseResourceJson(resourceJson)


if __name__ == '__main__':
    start = time.time()
    main()
