SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Table `languages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `languages`;

CREATE TABLE IF NOT EXISTS `languages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `language_code` VARCHAR(5) NOT NULL,
  `language_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Stores available languages like English (en) and Spanish (es).';

-- -----------------------------------------------------
-- Table `server_settings`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `server_settings`;

CREATE TABLE IF NOT EXISTS `server_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `guild_name` VARCHAR(100) NOT NULL,
  `owner_id` BIGINT NOT NULL,
  `member_count` INT NOT NULL,
  `prefix` VARCHAR(45) NOT NULL,
  `activated_events` TINYINT NOT NULL DEFAULT 1,
  `activated_logs` TINYINT NOT NULL DEFAULT 0,
  `activated_birthday` TINYINT NOT NULL DEFAULT 0,
  `birthday_channel` BIGINT NULL DEFAULT NULL,
  `logs_channel` BIGINT NULL DEFAULT NULL,
  `guild_language` INT NOT NULL,
  `default_bot_role_id` BIGINT NULL,
  `default_role_id` BIGINT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `guild_id_UNIQUE` (`guild_id` ASC) VISIBLE,
  CONSTRAINT `fk_guild_language`
    FOREIGN KEY (`guild_language`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores server-specific settings for AbbyBot.';

-- -----------------------------------------------------
-- Table `categories`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `categories`;

CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Stores categories for dialogues, like About Her, Lore, Advice.';

-- -----------------------------------------------------
-- Table `dialogues`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dialogues`;

CREATE TABLE IF NOT EXISTS `dialogues` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_dialogues_1_idx` (`language_id` ASC) VISIBLE,
  INDEX `fk_categories_idx` (`category_id` ASC) VISIBLE,
  CONSTRAINT `fk_languages`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_categories`
    FOREIGN KEY (`category_id`)
    REFERENCES `categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores dialogue messages that AbbyBot says in different languages.';

-- -----------------------------------------------------
-- Table `help`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `help`;

CREATE TABLE IF NOT EXISTS `help` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `command_code` VARCHAR(45) NOT NULL,
  `command_description` VARCHAR(255) NOT NULL,
  `usage` VARCHAR(255) NOT NULL,
  `language_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_language_id_idx` (`language_id` ASC) VISIBLE,
  CONSTRAINT `fk_language_id`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores help command descriptions for different languages.';

-- -----------------------------------------------------
-- Table `type_event_message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `type_event_message`;

CREATE TABLE IF NOT EXISTS `type_event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_message` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Stores types for event messages like normal, angry, forgive.';

-- -----------------------------------------------------
-- Table `event_message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `event_message`;

CREATE TABLE IF NOT EXISTS `event_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT NOT NULL,
  `language_id` INT NOT NULL,
  `message` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_type_idx` (`type_id` ASC) VISIBLE,
  INDEX `fk_language_idx` (`language_id` ASC) VISIBLE,
  CONSTRAINT `fk_type`
    FOREIGN KEY (`type_id`)
    REFERENCES `type_event_message` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_language`
    FOREIGN KEY (`language_id`)
    REFERENCES `languages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores event messages like mentions, deleted messages, etc.';

-- -----------------------------------------------------
-- Table `mention_counter`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mention_counter`;

CREATE TABLE IF NOT EXISTS `mention_counter` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `user_server` BIGINT NOT NULL,
  `mention_count` INT NOT NULL DEFAULT 0,
  `last_mention` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `index2` (`user_id` ASC, `user_server` ASC) VISIBLE,
  CONSTRAINT `fk_user_server`
    FOREIGN KEY (`user_server`)
    REFERENCES `server_settings` (`guild_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores mention counts per user per server.';

-- -----------------------------------------------------
-- Table `privileges`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `privileges`;

CREATE TABLE IF NOT EXISTS `privileges` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `privilege_name` VARCHAR(45) NOT NULL,
  `value` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Stores privilege levels for users.';

-- -----------------------------------------------------
-- Table `user_profile` (global user data)
-- -----------------------------------------------------

DROP TABLE IF EXISTS `user_profile`;

CREATE TABLE IF NOT EXISTS `user_profile` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `user_username` VARCHAR(45) NOT NULL,
  `user_birthday` DATE NULL DEFAULT NULL,
  `is_active` TINYINT NOT NULL DEFAULT 1,
  `user_privilege` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE (`user_id`),
  CONSTRAINT `fk_user_privilege`
    FOREIGN KEY (`user_privilege`)
    REFERENCES `privileges` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores global user data like birthday and privileges.';

-- -----------------------------------------------------
-- Table `dashboard` (server-specific user data)
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dashboard`;

CREATE TABLE IF NOT EXISTS `dashboard` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `user_profile_id` INT NOT NULL,  -- Links to user_profile
  `is_admin` TINYINT NOT NULL DEFAULT 0,
  `is_bot` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `fk_guild_userid_idx` (`guild_id` ASC),
  FOREIGN KEY (`user_profile_id`) REFERENCES `user_profile` (`id`),
  CONSTRAINT `fk_guild_userid`
    FOREIGN KEY (`guild_id`)
    REFERENCES `server_settings` (`guild_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Stores server-specific user data, like admin status.';

-- -----------------------------------------------------
-- Table `user_roles` (server-specific user roles)
-- -----------------------------------------------------
DROP TABLE IF EXISTS `user_roles`;

CREATE TABLE IF NOT EXISTS `user_roles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT NOT NULL,
  `user_profile_id` INT NOT NULL,  -- Links to user_profile
  `role_id` BIGINT NOT NULL,
  `role_name` VARCHAR(100) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_user_roles_1_idx` (`guild_id` ASC),
  FOREIGN KEY (`guild_id`) REFERENCES `server_settings` (`guild_id`),
  FOREIGN KEY (`user_profile_id`) REFERENCES `user_profile` (`id`)
) ENGINE = InnoDB
COMMENT = 'Stores user roles per server.';

-- Initial Data Inserts
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

INSERT INTO privileges (id, privilege_name, value)
VALUES
(1, 'Normal User 🐈', 1),
(2, 'Wishlist Contributor 🐧', 2),
(3, 'Developer Contributor 🧑‍💼', 3),
(4, 'Project Owner 👑', 4),
(5, 'AbbyBot 🧡', 5);

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
