# ************************************************************
# Sequel Pro SQL dump
# バージョン 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# ホスト: 127.0.0.1 (MySQL 5.6.21)
# データベース: money_mgr
# 作成時刻: 2015-06-29 02:20:08 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# テーブルのダンプ tbl_categories
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tbl_categories`;

CREATE TABLE `tbl_categories` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `type` tinyint(1) NOT NULL DEFAULT '0',
  `fixed` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `tbl_categories` WRITE;
/*!40000 ALTER TABLE `tbl_categories` DISABLE KEYS */;

INSERT INTO `tbl_categories` (`id`, `name`, `type`, `fixed`, `created`, `modified`)
VALUES
	(1,'給与',1,0,'2015-06-29 00:48:49','2015-06-29 00:48:49'),
	(2,'食費',0,0,'2015-06-29 00:49:00','2015-06-29 00:49:00'),
	(3,'電気代',0,1,'2015-06-29 00:49:12','2015-06-29 00:50:44'),
	(4,'ガス代',0,1,'2015-06-29 00:49:15','2015-06-29 00:50:41'),
	(5,'水道代',0,1,'2015-06-29 00:49:32','2015-06-29 00:50:37'),
	(6,'交通費',0,0,'2015-06-29 00:49:41','2015-06-29 00:49:41'),
	(7,'交際費',0,0,'2015-06-29 00:49:43','2015-06-29 00:49:43'),
	(8,'雑費',0,0,'2015-06-29 00:49:46','2015-06-29 00:49:46'),
	(9,'医療費',0,0,'2015-06-29 00:49:58','2015-06-29 00:49:58'),
	(10,'保険費',0,1,'2015-06-29 00:50:02','2015-06-29 00:50:26'),
	(11,'家賃',0,1,'2015-06-29 00:50:11','2015-06-29 00:50:21'),
	(12,'その他',0,0,'2015-06-29 00:50:17','2015-06-29 00:50:17');

/*!40000 ALTER TABLE `tbl_categories` ENABLE KEYS */;
UNLOCK TABLES;


# テーブルのダンプ tbl_creditcards
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tbl_creditcards`;

CREATE TABLE `tbl_creditcards` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `cutoff` int(11) NOT NULL DEFAULT '1',
  `debit` tinyint(1) NOT NULL DEFAULT '1',
  `member_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `tbl_creditcards` WRITE;
/*!40000 ALTER TABLE `tbl_creditcards` DISABLE KEYS */;

INSERT INTO `tbl_creditcards` (`id`, `name`, `cutoff`, `debit`, `member_id`, `created`, `modified`)
VALUES
	(1,'VISA',27,1,1,'2015-06-29 00:51:09','2015-06-29 00:51:09');

/*!40000 ALTER TABLE `tbl_creditcards` ENABLE KEYS */;
UNLOCK TABLES;


# テーブルのダンプ tbl_members
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tbl_members`;

CREATE TABLE `tbl_members` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `tbl_members` WRITE;
/*!40000 ALTER TABLE `tbl_members` DISABLE KEYS */;

INSERT INTO `tbl_members` (`id`, `name`, `created`, `modified`)
VALUES
	(1,'ユーザ1','2015-06-28 00:00:00','2015-06-28 00:00:00'),
	(2,'ユーザ2','2015-06-28 00:00:00','2015-06-28 00:00:00');

/*!40000 ALTER TABLE `tbl_members` ENABLE KEYS */;
UNLOCK TABLES;


# テーブルのダンプ tbl_payments
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tbl_payments`;

CREATE TABLE `tbl_payments` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `category_id` int(11) NOT NULL DEFAULT '0',
  `price` int(11) NOT NULL DEFAULT '0',
  `member_id` int(11) NOT NULL DEFAULT '0',
  `creditcard_id` int(11) DEFAULT '0',
  `date` datetime DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `tbl_payments` WRITE;
/*!40000 ALTER TABLE `tbl_payments` DISABLE KEYS */;

INSERT INTO `tbl_payments` (`id`, `name`, `category_id`, `price`, `member_id`, `creditcard_id`, `date`, `note`, `created`, `modified`)
VALUES
	(1,'家賃',11,75000,0,0,'2015-06-01 00:00:00','','2015-06-28 00:00:00','2015-06-29 01:16:20'),
	(2,'コンビニ',2,500,1,0,'2015-06-02 00:00:00','','2015-06-29 01:12:59','2015-06-29 01:12:59'),
	(3,'昼食',2,800,1,0,'2015-06-02 00:00:00','','2015-06-29 01:14:51','2015-06-29 01:14:51'),
	(5,'電気代',3,6000,0,0,'2015-06-01 00:00:00','','2015-06-29 01:17:43','2015-06-29 01:17:43'),
	(6,'ガス代',4,5000,0,0,'2015-06-01 00:00:00','','2015-06-29 01:17:57','2015-06-29 01:17:57'),
	(7,'夕食',2,1400,1,0,'2015-06-03 00:00:00','外食','2015-06-29 01:18:41','2015-06-29 01:18:41'),
	(8,'コンビニ',8,500,1,0,'2015-06-03 00:00:00','','2015-06-29 01:19:19','2015-06-29 01:19:19');

/*!40000 ALTER TABLE `tbl_payments` ENABLE KEYS */;
UNLOCK TABLES;


# テーブルのダンプ tbl_revenues
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tbl_revenues`;

CREATE TABLE `tbl_revenues` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `category_id` int(11) NOT NULL DEFAULT '0',
  `price` int(11) NOT NULL DEFAULT '0',
  `total_price` int(11) NOT NULL DEFAULT '0',
  `member_id` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `tbl_revenues` WRITE;
/*!40000 ALTER TABLE `tbl_revenues` DISABLE KEYS */;

INSERT INTO `tbl_revenues` (`id`, `name`, `category_id`, `price`, `total_price`, `member_id`, `date`, `note`, `created`, `modified`)
VALUES
	(1,'株式会社A',1,280000,320000,1,'2014-10-25 00:00:00','','2015-06-29 00:52:06','2015-06-29 00:52:06'),
	(2,'株式会社A',1,290000,330000,1,'2014-11-25 00:00:00','','2015-06-29 00:52:45','2015-06-29 00:52:45'),
	(3,'株式会社A',1,320000,380000,1,'2014-12-25 00:00:00','','2015-06-29 00:53:26','2015-06-29 00:53:26');

/*!40000 ALTER TABLE `tbl_revenues` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
