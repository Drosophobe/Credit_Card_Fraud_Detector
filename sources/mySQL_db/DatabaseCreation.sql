USE ccf_mysql;
-- We are creating the table from csv that will be our base
DROP TABLE IF EXISTS ccf_mysql.ccf_data_full;
CREATE TABLE ccf_mysql.ccf_data_full (
    distance_from_home FLOAT,
    distance_from_last_transaction FLOAT,
    ratio_to_median_purchase_price  FLOAT,
    repeat_retailer INTEGER,
    user_chip INTEGER,
    used_pin_number INTEGER,
    online_order INTEGER,
    fraud INTEGER);
LOAD DATA INFILE '/var/lib/mysql-files/card_transdata.csv'
INTO TABLE ccf_mysql.ccf_data_full
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r'
IGNORE 1 ROWS;
-- We are checking the Table previously created
SELECT * FROM ccf_mysql.ccf_data_full LIMIT 0, 10000000;
SELECT COUNT(*) FROM ccf_mysql.ccf_data_full;

-- We are creating a table with 0.1% of our data which will be used for the base model
DROP TABLE IF EXISTS ccf_mysql.ccf_data_partial;
CREATE TABLE ccf_mysql.ccf_data_partial (
    distance_from_home FLOAT,
    distance_from_last_transaction FLOAT,
    ratio_to_median_purchase_price  FLOAT,
    repeat_retailer INTEGER,
    user_chip INTEGER,
    used_pin_number INTEGER,
    online_order INTEGER,
    fraud INTEGER);
INSERT INTO ccf_mysql.ccf_data_partial SELECT * FROM ccf_mysql.ccf_data_full LIMIT 1000;
-- We are checking the Table previously created
SELECT * FROM ccf_mysql.ccf_data_partial;
SELECT COUNT(*) FROM ccf_mysql.ccf_data_partial;


-- We are copying the table with 0.1% of our data which will be used for train the new model and updated during production
DROP TABLE IF EXISTS ccf_mysql.ccf_data_i;
CREATE TABLE ccf_mysql.ccf_data_i (
    distance_from_home FLOAT,
    distance_from_last_transaction FLOAT,
    ratio_to_median_purchase_price  FLOAT,
    repeat_retailer INTEGER,
    user_chip INTEGER,
    used_pin_number INTEGER,
    online_order INTEGER,
    fraud INTEGER);
INSERT INTO ccf_mysql.ccf_data_i SELECT * FROM ccf_mysql.ccf_data_partial;
-- We are checking the Table previously created
SELECT * FROM ccf_mysql.ccf_data_i LIMIT 0, 1000000;
SELECT COUNT(*) FROM ccf_mysql.ccf_data_i;


-- We are creating a empty table that will be upaded with the corrected predictions to train model into production 
DROP TABLE IF EXISTS ccf_mysql.ccf_data_to_add;
CREATE TABLE ccf_mysql.ccf_data_to_add (
    distance_from_home FLOAT,
    distance_from_last_transaction FLOAT,
    ratio_to_median_purchase_price  FLOAT,
    repeat_retailer INTEGER,
    user_chip INTEGER,
    used_pin_number INTEGER,
    online_order INTEGER,
    fraud INTEGER);
-- We are checking the Table previously created
SELECT * FROM ccf_mysql.ccf_data_to_add;
-- Just a way to delte Table while testing
DELETE FROM ccf_mysql.ccf_data_to_add;


-- We are creating a table base on the base table that will be upaded by removing the values that the model already ingested 
DROP TABLE IF EXISTS ccf_mysql.ccf_data_remaining;
CREATE TABLE ccf_mysql.ccf_data_remaining (
    distance_from_home FLOAT,
    distance_from_last_transaction FLOAT,
    ratio_to_median_purchase_price  FLOAT,
    repeat_retailer INTEGER,
    user_chip INTEGER,
    used_pin_number INTEGER,
    online_order INTEGER,
    fraud INTEGER);
INSERT INTO ccf_mysql.ccf_data_remaining SELECT * FROM ccf_mysql.ccf_data_full;
-- we are deleting the first 0.1 values from ccf_data_i already ingested by the model
DELETE FROM ccf_data_remaining LIMIT 1000;
-- We are checking the Table previously created
SELECT * FROM ccf_mysql.ccf_data_remaining LIMIT 0, 10000000;
-- Checking the values to be deleted 
-- SELECT distance_from_home FROM ccf_data_remaining WHERE ROUND(distance_from_home, 4) IN (SELECT ROUND(distance_from_home, 4) FROM ccf_data_to_add) AND 
-- ROUND(distance_from_last_transaction, 4) IN (SELECT ROUND(distance_from_last_transaction, 4) FROM ccf_data_to_add) AND ROUND(ratio_to_median_purchase_price, 4) IN (SELECT 
-- ROUND(ratio_to_median_purchase_price, 4) FROM ccf_data_to_add);
-- we are deleting the values matching with ccf_data_to_add cause already sent to training 
-- DELETE  FROM ccf_data_remaining WHERE ROUND(distance_from_home, 4) IN (SELECT ROUND(distance_from_home, 4) FROM ccf_data_to_add) AND ROUND(distance_from_last_transaction, 4) IN 
-- (SELECT ROUND(distance_from_last_transaction, 4) FROM ccf_data_to_add) AND ROUND(ratio_to_median_purchase_price, 4) IN (SELECT ROUND(ratio_to_median_purchase_price, 4) FROM 
-- ccf_data_to_add);
SELECT distance_from_home FROM ccf_data_remaining WHERE ROUND(distance_from_home, 4) IN (SELECT ROUND(distance_from_home, 4) FROM ccf_data_to_add) AND ROUND(distance_from_last_transaction, 4) IN (SELECT ROUND(distance_from_last_transaction, 4) FROM ccf_data_to_add) AND ROUND(ratio_to_median_purchase_price, 4) IN (SELECT ROUND(ratio_to_median_purchase_price, 4) FROM ccf_data_to_add);
