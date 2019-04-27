/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50717
Source Host           : localhost:3306
Source Database       : jd

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2019-04-27 23:45:25
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for jd_help
-- ----------------------------
DROP TABLE IF EXISTS `jd_help`;
CREATE TABLE `jd_help` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `coupon` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ccount` int(100) DEFAULT NULL,
  `keyid` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `roleid` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `batchid` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `usetime` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of jd_help
-- ----------------------------
INSERT INTO `jd_help` VALUES ('1', '仅可购买海囤全球自营a2奶粉部分商品999-500', '200', '7853430d27e34edeb5c61a02c158c058', '18982121', 'https://search.jd.com/Search?https://search.jd.com/Search?coupon_batch=200902474', '2019-04-17 00:00:00----2019-04-17 23:59:59');

-- ----------------------------
-- Table structure for re_port
-- ----------------------------
DROP TABLE IF EXISTS `re_port`;
CREATE TABLE `re_port` (
  `id` tinyint(10) NOT NULL AUTO_INCREMENT,
  `port` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of re_port
-- ----------------------------
INSERT INTO `re_port` VALUES ('1', 'https://plus.m.jd.com/coupon/receiveCoupon?activeKey={2}&roleId={0}');
INSERT INTO `re_port` VALUES ('2', 'https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&body={{%22activityId%22:%2225N4bVkmMV4S2RL61A8DYNwqD8Vv%22,%22from%22:%22H5node%22,%22scene%22:%221%22,%22args%22:%22key={2},roleId={0}%22}}&client=wh5&clientVersion=1.0.0&callback=jsonp2');
INSERT INTO `re_port` VALUES ('3', 'https://act-jshop.jd.com/couponSend.html?callback=jQuery5047673&ruleId={0}&key={2}&platform=0');
