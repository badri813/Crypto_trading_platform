create database mycrypto_2;
use mycrypto_2;  

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    status VARCHAR(255)
);



CREATE TABLE crypto_price (
    crypto_price_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(255),
    current_price VARCHAR(255),
    fiat_currency VARCHAR(255)
);




CREATE TABLE transactions (
  transaction_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  crypto_price_id INT,
  number_of_coins DECIMAL(18,8),
  amount DECIMAL(15,8),
  cost DECIMAL(15,2),
  transaction_type ENUM('buy', 'sell', 'p2p-buy', 'p2p-sell'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (crypto_price_id) REFERENCES crypto_price(crypto_price_id)
);


create table wallet(
wallet_id int AUTO_INCREMENT PRIMARY KEY,
user_id INT,
amount VARCHAR(255) NOT NULL  DEFAULT '0',
FOREIGN KEY (user_id) REFERENCES users(user_id)
);


create TABLE p2p_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(15,8) NOT NULL,
    payment_mode ENUM('Wallet', 'Bank') NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id int,
    foreign key (transaction_id) references  transactions (transaction_id)
);


CREATE TABLE crypto_data (
    crypto_data_id INT AUTO_INCREMENT PRIMARY KEY,
    Date DATE NOT NULL,
    Ticker VARCHAR(20) NOT NULL,
    Open DOUBLE,
    High DOUBLE,
    Low DOUBLE,
    Close DOUBLE,
    Volume BIGINT,
    percentage_change DOUBLE
);


CREATE TABLE sentiment_scores (
    sentiment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    avg_sentiment_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE image_icon (
    image_icon_id INT AUTO_INCREMENT PRIMARY KEY,
    image_name VARCHAR(255) NOT NULL
);


CREATE TABLE  rsi_summary (
	rsi_summary_id INT AUTO_INCREMENT PRIMARY KEY,
    Ticker VARCHAR(20),
    Total INT,
    Overbought INT,
    Oversold INT,
    OverboughtPercent FLOAT,
    OversoldPercent FLOAT
);


