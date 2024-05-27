-- MySQL Script generated by MySQL Workbench
-- Fri May 24 17:18:49 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema epicevents
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema epicevents
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `epicevents` DEFAULT CHARACTER SET utf8 ;
USE `epicevents` ;

-- -----------------------------------------------------
-- Table `epicevents`.`Department`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `epicevents`.`Department` (
  `id` INT NOT NULL,
  `name` VARCHAR(50) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `epicevents`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `epicevents`.`User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NULL,
  `password` VARCHAR(255) NULL,
  `email` VARCHAR(100) NULL,
  `name` VARCHAR(50) NULL,
  `department_id` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  INDEX `department_id_idx` (`department_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_department`
    FOREIGN KEY (`department_id`)
    REFERENCES `epicevents`.`Department` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `epicevents`.`Client`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `epicevents`.`Client` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(100) NULL,
  `email` VARCHAR(100) NULL,
  `phone` VARCHAR(20) NULL,
  `company_name` VARCHAR(100) NULL,
  `date_created` DATE NULL,
  `last_contact_date` DATE NULL,
  `commercial_contact_id` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  INDEX `commercial_contact_id_idx` (`commercial_contact_id` ASC) VISIBLE,
  CONSTRAINT `fk_client_commercial_contact`
    FOREIGN KEY (`commercial_contact_id`)
    REFERENCES `epicevents`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `epicevents`.`Contract`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `epicevents`.`Contract` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `client_id` INT NULL,
  `commercial_contact_id` INT NULL,
  `total_amount` DECIMAL(10,2) NULL,
  `amount_due` DECIMAL(10,2) NULL,
  `date_created` DATE NULL,
  `signed` TINYINT NULL,
  PRIMARY KEY (`id`),
  INDEX `client_id_idx` (`client_id` ASC) VISIBLE,
  INDEX `commercial_contact_id_idx` (`commercial_contact_id` ASC) VISIBLE,
  CONSTRAINT `fk_contract_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `epicevents`.`Client` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contract_commercial_contact`
    FOREIGN KEY (`commercial_contact_id`)
    REFERENCES `epicevents`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `epicevents`.`Event`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `epicevents`.`Event` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contract_id` INT NOT NULL,
  `client_id` INT NULL,
  `event_name` VARCHAR(100) NULL,
  `event_date_start` DATE NULL,
  `event_date_end` DATE NULL,
  `support_contact_id` INT NULL,
  `location` VARCHAR(200) NULL,
  `attendees` INT NULL,
  `notes` LONGTEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `client_id_idx` (`client_id` ASC) VISIBLE,
  INDEX `support_contact_id_idx` (`support_contact_id` ASC) VISIBLE,
  UNIQUE INDEX `contract_id_UNIQUE` (`contract_id` ASC) VISIBLE,
  CONSTRAINT `fk_event_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `epicevents`.`Client` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_event_support_contact`
    FOREIGN KEY (`support_contact_id`)
    REFERENCES `epicevents`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_event_contract`
    FOREIGN KEY (`contract_id`)
    REFERENCES `epicevents`.`Contract` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
