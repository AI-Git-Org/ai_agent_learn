-- Create Database
CREATE DATABASE IF NOT EXISTS financial_db;
USE financial_db;

-- Currency Master
CREATE TABLE IF NOT EXISTS Tb_ccy_master (
    Currency_code VARCHAR(3) NOT NULL,
    Day_count VARCHAR(20) NOT NULL,
    PRIMARY KEY (Currency_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Legal Entity Master
CREATE TABLE IF NOT EXISTS Tb_LE_code (
    LE_code VARCHAR(20) NOT NULL,
    LE_desc VARCHAR(255) NOT NULL,
    PRIMARY KEY (LE_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Contract Balance
CREATE TABLE IF NOT EXISTS Tb_contract_balance (
    id INT AUTO_INCREMENT,
    As_of_date DATE NOT NULL,
    Start_date DATE NULL,
    End_date DATE NULL,
    Amt DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
    Cust_rate DECIMAL(10,6),
    PnL DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
    Currency VARCHAR(3) NOT NULL,

    PRIMARY KEY (id, As_of_date),

    CONSTRAINT fk_contract_ccy
    FOREIGN KEY (Currency)
    REFERENCES Tb_ccy_master(Currency_code)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Use Rate
CREATE TABLE IF NOT EXISTS Tb_use_rate (
    id INT AUTO_INCREMENT,
    As_of_rate DATE NOT NULL,
    yc_code VARCHAR(20) NOT NULL,
    Bid_rate DECIMAL(10,6),
    Offer_rate DECIMAL(10,6),
    Tenure VARCHAR(20),
    Currency VARCHAR(3) NOT NULL,

    PRIMARY KEY (id, As_of_rate),

    CONSTRAINT fk_use_rate_ccy
    FOREIGN KEY (Currency)
    REFERENCES Tb_ccy_master(Currency_code)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Ticket Balance
CREATE TABLE IF NOT EXISTS Tb_ticket_balance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    As_of_date DATE NOT NULL,
    Start_date DATE NULL,
    End_date DATE NULL,
    Amt DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
    TP_rate DECIMAL(10,6),
    PnL DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
    Currency VARCHAR(3) NOT NULL,

    CONSTRAINT fk_ticket_ccy
    FOREIGN KEY (Currency)
    REFERENCES Tb_ccy_master(Currency_code)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- TP Rate
CREATE TABLE IF NOT EXISTS Tb_TP_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    As_of_date DATE NOT NULL,
    Start_date DATE NULL,
    End_date DATE NULL,
    Bid_rate DECIMAL(10,6),
    Offer_rate DECIMAL(10,6),
    Tenure VARCHAR(20),
    Currency VARCHAR(3) NOT NULL,

    CONSTRAINT fk_tp_rate_ccy
    FOREIGN KEY (Currency)
    REFERENCES Tb_ccy_master(Currency_code)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;