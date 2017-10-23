-- MySQL dump 10.13  Distrib 5.5.57, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ciresources
-- ------------------------------------------------------
-- Server version	5.5.57-0ubuntu0.14.04.1

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
INSERT INTO `cimc_baremetals` VALUES (1,'192.133.149.18','1/7',0,'2017-10-23 17:05:27','cc:16:7e:1e:e9:76'),(2,'192.133.149.17','1/5',0,NULL,'cc:16:7e:91:41:67'),(3,'192.133.149.16','1/3',0,NULL,'58:97:bd:e5:f6:b3'),(4,'192.133.149.15','1/1',0,NULL,'a0:36:9f:20:61:78');
/*!40000 ALTER TABLE `cimc_baremetals` ENABLE KEYS */;
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
INSERT INTO `vlans` VALUES (2000,2100,0,'2017-10-23 17:05:19'),(2101,2200,0,'2017-10-23 13:18:08'),(2201,2300,0,'2017-10-23 13:19:26'),(2301,2400,0,'2017-10-23 13:19:43'),(2401,2500,0,'2017-10-23 13:43:12'),(2501,2550,0,'2017-10-23 13:20:32'),(2551,2600,0,'2017-10-23 13:20:44'),(2601,2650,0,'2017-10-23 13:20:46'),(2651,2700,0,'2017-10-23 13:38:45'),(2701,2750,0,'2017-10-19 14:10:55'),(2751,2800,0,'2017-10-19 14:11:08'),(2801,2850,0,'2017-10-19 14:11:08'),(2851,2900,0,'2017-10-19 14:11:11'),(2901,2950,0,'2017-10-19 14:24:25'),(2951,3000,0,NULL),(3001,3050,0,NULL),(3051,3100,0,NULL),(3101,3150,0,NULL),(3151,3200,0,NULL),(3201,3250,0,NULL),(3251,3300,0,NULL),(3301,3350,0,NULL),(3351,3400,0,NULL),(3401,3450,0,NULL),(3451,3500,0,NULL);
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

-- Dump completed on 2017-10-23 13:11:00
