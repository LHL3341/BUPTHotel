CREATE TABLE `log_entry` (
	`room` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`request_time` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`start_time` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`end_time` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`duration` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`speed` INT(11) NOT NULL,
	`period_cost` FLOAT NOT NULL,
	`fee_rate` FLOAT NOT NULL,
	`from_tem` FLOAT NOT NULL DEFAULT '0',
	`to_tem` FLOAT NOT NULL DEFAULT '0',
	PRIMARY KEY (`request_time`, `start_time`, `end_time`) USING BTREE
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;