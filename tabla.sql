/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.6.23-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: Aventura
-- ------------------------------------------------------
-- Server version	10.6.23-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `camins`
--

DROP TABLE IF EXISTS `camins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `camins` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom1` varchar(50) NOT NULL,
  `localitzacio1` bigint(20) unsigned NOT NULL,
  `localitzacio2` bigint(20) unsigned NOT NULL,
  `nom2` varchar(50) NOT NULL,
  `tancat` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camins`
--

LOCK TABLES `camins` WRITE;
/*!40000 ALTER TABLE `camins` DISABLE KEYS */;
INSERT INTO `camins` VALUES (6,'Huge door',13,14,'Door to Street',1);
/*!40000 ALTER TABLE `camins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combinacions`
--

DROP TABLE IF EXISTS `combinacions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `combinacions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `objecte_a` bigint(20) NOT NULL,
  `objecte_b` bigint(20) NOT NULL,
  `resultat_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `objecte_a` (`objecte_a`),
  KEY `objecte_b` (`objecte_b`),
  KEY `resultat_id` (`resultat_id`),
  CONSTRAINT `combinacions_ibfk_1` FOREIGN KEY (`objecte_a`) REFERENCES `objectes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `combinacions_ibfk_2` FOREIGN KEY (`objecte_b`) REFERENCES `objectes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `combinacions_ibfk_3` FOREIGN KEY (`resultat_id`) REFERENCES `objectes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combinacions`
--

LOCK TABLES `combinacions` WRITE;
/*!40000 ALTER TABLE `combinacions` DISABLE KEYS */;
/*!40000 ALTER TABLE `combinacions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interaccions`
--

DROP TABLE IF EXISTS `interaccions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `interaccions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `objecte_id` bigint(20) NOT NULL,
  `target_tipus` enum('objecte','cami') NOT NULL,
  `target_id` bigint(20) NOT NULL,
  `resultat_tipus` enum('obrir_cami','crear_objecte','missatge') NOT NULL,
  `resultat_id` bigint(20) DEFAULT NULL,
  `resultat_missatge` varchar(250) DEFAULT NULL,
  `consumeix` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `objecte_id` (`objecte_id`),
  CONSTRAINT `interaccions_ibfk_1` FOREIGN KEY (`objecte_id`) REFERENCES `objectes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interaccions`
--

LOCK TABLES `interaccions` WRITE;
/*!40000 ALTER TABLE `interaccions` DISABLE KEYS */;
/*!40000 ALTER TABLE `interaccions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `localitzacions`
--

DROP TABLE IF EXISTS `localitzacions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `localitzacions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `descripcio` text DEFAULT NULL,
  `imatge` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `localitzacions`
--

LOCK TABLES `localitzacions` WRITE;
/*!40000 ALTER TABLE `localitzacions` DISABLE KEYS */;
INSERT INTO `localitzacions` VALUES (13,'Street','Full of zombies','/static/img/street.jpg'),(14,'Main Hall','It\'s huge','/static/img/main_hall.jpg');
/*!40000 ALTER TABLE `localitzacions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `objectes`
--

DROP TABLE IF EXISTS `objectes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `objectes` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `descripcio` text DEFAULT NULL,
  `imatge` varchar(250) DEFAULT NULL,
  `localitzacio_id` bigint(20) DEFAULT NULL,
  `pos_x` float DEFAULT 50,
  `pos_y` float DEFAULT 50,
  `agafable` tinyint(1) NOT NULL DEFAULT 1,
  `usos` int(11) NOT NULL DEFAULT -1,
  PRIMARY KEY (`id`),
  KEY `localitzacio_id` (`localitzacio_id`),
  CONSTRAINT `objectes_ibfk_1` FOREIGN KEY (`localitzacio_id`) REFERENCES `localitzacions` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `objectes`
--

LOCK TABLES `objectes` WRITE;
/*!40000 ALTER TABLE `objectes` DISABLE KEYS */;
/*!40000 ALTER TABLE `objectes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-15 13:53:23
