-- MySQL Generic Script

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- Drop existing tables if they exist
DROP TABLE IF EXISTS `languages`;
DROP TABLE IF EXISTS `server_settings`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `dialogues`;
DROP TABLE IF EXISTS `help`;
DROP TABLE IF EXISTS `type_event_message`;
DROP TABLE IF EXISTS `event_message`;
DROP TABLE IF EXISTS `mention_counter`;
DROP TABLE IF EXISTS `dashboard`;

-- Table: languages
CREATE TABLE IF NOT EXISTS `languages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `language_code` VARCHAR(5) NOT NULL,
  `language_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- Table: server_settings
CREATE TABLE IF NOT EXISTS `server_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `guild_name` VARCHAR(100) NOT NULL,
  `owner_id` BIGINT NOT NULL,
  `member_count` INT NOT NULL,
  `prefix` VARCHAR(45) NOT NULL,
  `activated_events` TINYINT NOT NULL DEFAULT 1,
  `activated_logs` TINYINT NOT NULL DEFAULT 1,
  `logs_channel` BIGINT NULL DEFAULT NULL,
  `guild_language` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_guild_language_idx` (`guild_language` ASC),
  UNIQUE INDEX `guild_id_UNIQUE` (`guild_id` ASC),
  CONSTRAINT `fk_guild_language`
    FOREIGN KEY (`guild_language`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Table: categories
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- Table: dialogues
CREATE TABLE IF NOT EXISTS `dialogues` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_dialogues_1_idx` (`language_id` ASC),
  INDEX `fk_categories_idx` (`category_id` ASC),
  CONSTRAINT `fk_languages`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_categories`
    FOREIGN KEY (`category_id`)
    REFERENCES `categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Table: help
CREATE TABLE IF NOT EXISTS `help` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `command_code` VARCHAR(45) NOT NULL,
  `command_description` VARCHAR(255) NOT NULL,
  `language_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_language_id_idx` (`language_id` ASC),
  CONSTRAINT `fk_language_id`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Table: type_event_message
CREATE TABLE IF NOT EXISTS `type_event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_message` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- Table: event_message
CREATE TABLE IF NOT EXISTS `event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_type_idx` (`type_id` ASC),
  INDEX `fk_language_idx` (`language_id` ASC),
  CONSTRAINT `fk_type`
    FOREIGN KEY (`type_id`)
    REFERENCES `type_event_message` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_language`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Table: mention_counter
CREATE TABLE IF NOT EXISTS `mention_counter` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `user_server` BIGINT NOT NULL,
  `mention_count` INT NOT NULL DEFAULT 0,
  `last_mention` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `index2` (`user_id`, `user_server` ASC),
  CONSTRAINT `fk_user_server`
    FOREIGN KEY (`user_server`)
    REFERENCES `server_settings` (`guild_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Table: dashboard
CREATE TABLE IF NOT EXISTS `dashboard` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `user_id` BIGINT NOT NULL,
  `user_username` VARCHAR(45) NOT NULL,
  `user_nickname` VARCHAR(45) NOT NULL,
  `date_joined` TIMESTAMP NULL DEFAULT NULL,
  `user_birthday` DATE NULL DEFAULT NULL,
  `is_active` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  INDEX `fk_guild_userid_idx` (`guild_id` ASC),
  CONSTRAINT `fk_guild_userid`
    FOREIGN KEY (`guild_id`)
    REFERENCES `server_settings` (`guild_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;


INSERT INTO languages (id, language_code, language_name)
VALUES
(1, 'en', 'English'),
(2, 'es', 'Español');


INSERT INTO categories (id, category)
VALUES
(1, 'About Her'),
(2, 'Lore'),
(3, 'Advice');


INSERT INTO type_event_message (id, type_message)
VALUES
(1, 'normal'),
(2, 'angry'),
(3, 'forgive');


-- Restore previous settings
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;



