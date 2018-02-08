-- MySQL dump 10.13  Distrib 5.5.59, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ciresources
-- ------------------------------------------------------
-- Server version	5.5.59-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cimc_baremetals`
--

DROP TABLE IF EXISTS `cimc_baremetals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cimc_baremetals` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `bmc_address` varchar(255) NOT NULL,
  `nexus_port` varchar(255) NOT NULL,
  `locked` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT NULL,
  `mac_address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `bmc_address` (`bmc_address`),
  UNIQUE KEY `nexus_port` (`nexus_port`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cimc_baremetals`
--

LOCK TABLES `cimc_baremetals` WRITE;
/*!40000 ALTER TABLE `cimc_baremetals` DISABLE KEYS */;
INSERT INTO `cimc_baremetals` VALUES (1,'192.133.149.18','1/7',1,'2018-02-14 11:18:21','cc:16:7e:1e:e9:76'),(2,'192.133.149.17','1/5',0,'2018-02-14 11:55:16','cc:16:7e:91:41:67'),(3,'192.133.149.16','1/3',1,'2018-02-14 12:08:02','58:97:bd:e5:f6:b3'),(4,'192.133.149.15','1/1',1,'2018-02-13 12:33:08','90:e2:ba:45:9e:49');
/*!40000 ALTER TABLE `cimc_baremetals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `region_ids`
--

DROP TABLE IF EXISTS `region_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_ids` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `region_id` varchar(255) NOT NULL,
  `locked` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `region_id` (`region_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `region_ids`
--

LOCK TABLES `region_ids` WRITE;
/*!40000 ALTER TABLE `region_ids` DISABLE KEYS */;
INSERT INTO `region_ids` VALUES (1,'L3FR002',0,'2018-02-13 04:36:47'),(2,'L3FR003',0,'2017-10-23 17:05:27'),(3,'L3FR004',0,'2017-10-23 17:05:27'),(4,'L3FR005',0,'2017-10-23 17:05:27'),(5,'L3FR006',0,'2017-10-23 17:05:27'),(6,'L3FR007',0,'2017-10-23 17:05:27'),(7,'L3FR008',0,'2017-10-23 17:05:27'),(8,'L3FR009',0,'2017-10-23 17:05:27'),(9,'L3FR010',0,'2017-10-23 17:05:27'),(10,'L3FR011',0,'2017-10-23 17:05:27'),(11,'L3FR012',0,'2017-10-23 17:05:27'),(12,'L3FR013',0,'2017-10-23 17:05:27'),(13,'L3FR014',0,'2017-10-23 17:05:27'),(14,'L3FR015',0,'2017-10-23 17:05:27'),(15,'L3FR016',0,'2017-10-23 17:05:27'),(16,'L3FR017',0,'2017-10-23 17:05:27'),(17,'L3FR018',0,'2017-10-23 17:05:27'),(18,'L3FR019',0,'2017-10-23 17:05:27'),(19,'L3FR020',0,'2017-10-23 17:05:27'),(20,'L3FR021',0,'2017-10-23 17:05:27'),(21,'L3FR022',0,'2017-10-23 17:05:27');
/*!40000 ALTER TABLE `region_ids` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ucsm_baremetals`
--

DROP TABLE IF EXISTS `ucsm_baremetals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ucsm_baremetals` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `bmc_address` varchar(255) DEFAULT NULL,
  `service_profile` varchar(255) NOT NULL,
  `mac_address` varchar(225) NOT NULL,
  `locked` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ucsm_baremetals`
--

LOCK TABLES `ucsm_baremetals` WRITE;
/*!40000 ALTER TABLE `ucsm_baremetals` DISABLE KEYS */;
INSERT INTO `ucsm_baremetals` VALUES (5,'192.133.149.19','ironic-node-1','00:25:B5:00:00:02',0,NULL),(6,'192.133.149.19','ironic-node-2','00:25:B5:00:00:01',0,NULL),(7,'192.133.149.19','ironic-node-3','00:25:B5:00:00:00',0,NULL);
/*!40000 ALTER TABLE `ucsm_baremetals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vlans`
--

DROP TABLE IF EXISTS `vlans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vlans` (
  `min_vlan` smallint(5) unsigned NOT NULL,
  `max_vlan` smallint(5) unsigned NOT NULL,
  `locked` tinyint(1) NOT NULL DEFAULT '0',
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`min_vlan`,`max_vlan`),
  UNIQUE KEY `min_vlan` (`min_vlan`),
  UNIQUE KEY `max_vlan` (`max_vlan`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vlans`
--

LOCK TABLES `vlans` WRITE;
/*!40000 ALTER TABLE `vlans` DISABLE KEYS */;
INSERT INTO `vlans` VALUES (2000,2100,1,'2018-02-14 11:18:10'),(2101,2200,1,'2018-02-14 12:27:24'),(2201,2300,1,'2018-02-14 11:54:14'),(2301,2400,1,'2018-02-14 11:54:16'),(2401,2500,0,'2018-02-14 11:55:06'),(2501,2550,0,'2018-02-14 11:55:34'),(2551,2600,0,'2018-02-14 11:55:53'),(2601,2650,0,'2018-02-14 11:56:00'),(2651,2700,0,'2018-02-14 11:56:22'),(2701,2750,1,'2018-02-14 11:56:43'),(2751,2800,1,'2018-02-14 11:56:47'),(2801,2850,1,'2018-02-14 11:56:56'),(2851,2900,1,'2018-02-14 12:07:53'),(2901,2950,0,'2018-02-12 21:31:23'),(2951,3000,0,'2018-02-12 21:31:35'),(3001,3050,0,'2018-02-12 21:31:38'),(3051,3100,0,'2017-12-11 16:39:33'),(3101,3150,0,NULL),(3151,3200,0,NULL),(3201,3250,0,NULL),(3251,3300,0,NULL),(3301,3350,0,NULL),(3351,3400,0,NULL),(3401,3450,0,NULL),(3451,3500,0,NULL);
/*!40000 ALTER TABLE `vlans` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-02-14  7:27:07
