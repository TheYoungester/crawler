CREATE TABLE `config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `type` int(255) NOT NULL COMMENT '1.search tag of ins',
  PRIMARY KEY (`id`) USING BTREE
)
INSERT INTO `config` VALUES (1, '手账', 1);
INSERT INTO `config` VALUES (2, '手掌', 1);
INSERT INTO `config` VALUES (3, '收账', 1);
INSERT INTO `config` VALUES (4, '手帳', 1);
INSERT INTO `config` VALUES (5, 'bulletjournal', 1);
INSERT INTO `config` VALUES (6, 'bulletjournals', 1);
INSERT INTO `config` VALUES (7, 'brushinglettering', 1);

CREATE TABLE `insgram`  (
  `graphql_id` int(64) NOT NULL COMMENT 'tag的编号',
  `graphql_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `graphql_allow_following` int(255) NOT NULL COMMENT '1.search tag of ins',
  `graphql_count` int(255) NOT NULL COMMENT '帖子总数',
  `graphql_rofile_pic_url` varchar(255) NOT NULL COMMENT '封面图片地址',
  PRIMARY KEY (`id`) USING BTREE
)

INSERT INTO `hashtag` VALUES ('1', '1', 1, 1, 1, '1', 1);
INSERT INTO `edge_hashtag_to_media` VALUES ('1', '1', '1', 1, '2019-11-21 17:42:03', 1, 1, '1', 1, 1, '1', '1', 1, '1');
INSERT INTO `crawler`.`edge_hashtag_to_media`(`id`, `hashtag_id`, `shortcode`, `edge_media_to_comment`, `taken_at_timestamp`, `height`, `width`, `display_url`, `edge_liked_by`, `edge_media_preview_like`, `owner`, `thumbnail_src`, `is_video`, `accessibility_caption`) VALUES ('1', '1', '1', 1, '1233', 1, 1, '1', 1, 1, '1', '1', 1, '1');
