-- -----------------------------------------------------
-- Table `abbybot`.`server_settings`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`server_settings` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`server_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `guild_name` VARCHAR(100) NOT NULL,
  `owner_id` BIGINT NOT NULL,
  `member_count` INT NOT NULL,
  `prefix` VARCHAR(45) NOT NULL,
  `guild_language` VARCHAR(5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `guild_id_UNIQUE` (`guild_id` ASC) VISIBLE)
ENGINE = InnoDB
COMMENT = 'In this table all servers that use AbbyBot will be registered.';


-- -----------------------------------------------------
-- Table `abbybot`.`languages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`languages` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`languages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `language_code` VARCHAR(5) NOT NULL,
  `language_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'In this table, language list will be saved, in this case only \'en\' English and \'es\' Spanish.';


-- -----------------------------------------------------
-- Table `abbybot`.`categories`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`categories` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'In this table the categories for the messages that the \'dialogues\' table will have will be stored.';


-- -----------------------------------------------------
-- Table `abbybot`.`dialogues`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`dialogues` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`dialogues` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_dialogues_1_idx` (`language_id` ASC) VISIBLE,
  INDEX `fk_categories_idx` (`category_id` ASC) VISIBLE,
  CONSTRAINT `fk_languages`
    FOREIGN KEY (`language_id`)
    REFERENCES `abbybot`.`languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_categories`
    FOREIGN KEY (`category_id`)
    REFERENCES `abbybot`.`categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'In dialogues table, all quotes that AbbyBot says are saved, in all languages.';


-- -----------------------------------------------------
-- Table `abbybot`.`help`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`help` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`help` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `command_code` VARCHAR(45) NOT NULL,
  `command_description` VARCHAR(255) NOT NULL,
  `language_code` VARCHAR(5) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'In this table all help commands will be registered, in this moment manually.';


-- -----------------------------------------------------
-- Table `abbybot`.`type_event_message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`type_event_message` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`type_event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_message` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'In this table are saved the types for event_message table.';


-- -----------------------------------------------------
-- Table `abbybot`.`event_message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `abbybot`.`event_message` ;

CREATE TABLE IF NOT EXISTS `abbybot`.`event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_type_idx` (`type_id` ASC) VISIBLE,
  INDEX `fk_language_idx` (`language_id` ASC) VISIBLE,
  CONSTRAINT `fk_type`
    FOREIGN KEY (`type_id`)
    REFERENCES `abbybot`.`type_event_message` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_language`
    FOREIGN KEY (`language_id`)
    REFERENCES `abbybot`.`languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'In this table event messages like mentions or deleted messages are registered.';

