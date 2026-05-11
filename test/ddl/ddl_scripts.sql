-- Create database
CREATE DATABASE IF NOT EXISTS meal_prediction
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE meal_prediction;

-- meal_prediction.age_prefs definition

CREATE TABLE `age_prefs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `age_group` varchar(30) NOT NULL,
  `pork` float DEFAULT NULL,
  `chicken` float DEFAULT NULL,
  `beef` float DEFAULT NULL,
  `seafood` float DEFAULT NULL,
  `lamb` float DEFAULT NULL,
  `vegetarian` float DEFAULT NULL,
  `reasoning` text,
  `sources` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `age_group` (`age_group`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.alembic_version definition

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.customers definition

CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `operating_flight_number` varchar(20) NOT NULL,
  `segment` varchar(20) NOT NULL,
  `cabin_class` varchar(5) NOT NULL,
  `departure_airport` varchar(10) NOT NULL,
  `arrival_airport` varchar(10) NOT NULL,
  `destination_region` varchar(100) DEFAULT NULL,
  `nationality_code` varchar(10) DEFAULT NULL,
  `age_group` varchar(20) DEFAULT NULL,
  `meal_time` varchar(30) DEFAULT NULL,
  `customer_number` varchar(128) DEFAULT NULL,
  `segment_local_departure_datetime` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_customers_operating_flight_number` (`operating_flight_number`),
  KEY `ix_customer_flight_date` (`operating_flight_number`,`segment_local_departure_datetime`)
) ENGINE=InnoDB AUTO_INCREMENT=1198828 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.destination_prefs definition

CREATE TABLE `destination_prefs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `airport_code` varchar(10) NOT NULL,
  `destination_region` varchar(100) NOT NULL,
  `pork` float DEFAULT NULL,
  `chicken` float DEFAULT NULL,
  `beef` float DEFAULT NULL,
  `seafood` float DEFAULT NULL,
  `lamb` float DEFAULT NULL,
  `vegetarian` float DEFAULT NULL,
  `reasoning` text,
  `sources` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `airport_code` (`airport_code`),
  KEY `ix_dest_region` (`destination_region`)
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.meals definition

CREATE TABLE `meals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `segment` varchar(20) NOT NULL,
  `segment_local_departure_date` varchar(20) NOT NULL,
  `cabin_class` varchar(5) NOT NULL,
  `meal_time` varchar(30) NOT NULL,
  `meal_name` text,
  `meal_pref` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_meal_segment_date` (`segment`,`segment_local_departure_date`)
) ENGINE=InnoDB AUTO_INCREMENT=58159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.mealtime_prefs definition

CREATE TABLE `mealtime_prefs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `meal_time` varchar(30) NOT NULL,
  `pork` float DEFAULT NULL,
  `chicken` float DEFAULT NULL,
  `beef` float DEFAULT NULL,
  `seafood` float DEFAULT NULL,
  `lamb` float DEFAULT NULL,
  `vegetarian` float DEFAULT NULL,
  `reasoning` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `meal_time` (`meal_time`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.nationality_prefs definition

CREATE TABLE `nationality_prefs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nationality_code` varchar(10) NOT NULL,
  `day_of_week` varchar(15) NOT NULL,
  `pork` float DEFAULT NULL,
  `chicken` float DEFAULT NULL,
  `beef` float DEFAULT NULL,
  `seafood` float DEFAULT NULL,
  `lamb` float DEFAULT NULL,
  `vegetarian` float DEFAULT NULL,
  `reasoning` text,
  `sources` text,
  PRIMARY KEY (`id`),
  KEY `ix_nat_pref_code_day` (`nationality_code`,`day_of_week`)
) ENGINE=InnoDB AUTO_INCREMENT=1534 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- meal_prediction.prediction_history definition

CREATE TABLE `prediction_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `segment` varchar(20) NOT NULL,
  `segment_local_departure_date` varchar(20) NOT NULL,
  `cabin_class` varchar(5) NOT NULL,
  `meal_time` varchar(30) NOT NULL,
  `protein_type` varchar(30) NOT NULL,
  `original_meal_count` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_pred_history_segment_date` (`segment`,`segment_local_departure_date`,`cabin_class`,`meal_time`)
) ENGINE=InnoDB AUTO_INCREMENT=18355 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;