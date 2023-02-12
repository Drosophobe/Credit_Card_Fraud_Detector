import mysql.connector
from mysql.connector import errorcode
from unittest import TestCase
from mock import patch
import db_utils_data

MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "ccf_data"
MYSQL_PORT = "3306"

class MockDB(TestCase):

    @classmethod
    def setUpClass(cls):
        cnx = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port = MYSQL_PORT
        )
        cursor = cnx.cursor(dictionary=True)

        # drop database if it already exists
        try:
            cursor.execute("DROP DATABASE {}".format(MYSQL_DB))
            cursor.close()
            print("DB dropped")
        except mysql.connector.Error as err:
            print("{}{}".format(MYSQL_DB, err))

        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(MYSQL_DB))
            print("DB Created")
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)
        cnx.database = MYSQL_DB
        for table in ["ccf_data_full", "ccf_data_partial", "ccf_data_i", "ccf_data_remaining", "ccf_data_to_add"]:
            print(table)
            cursor = cnx.cursor(dictionary=True)
        
            query = f"""CREATE TABLE {MYSQL_DB}.{table} (
                    distance_from_home FLOAT,
                    distance_from_last_transaction FLOAT,
                    ratio_to_median_purchase_price  FLOAT,
                    repeat_retailer INTEGER,
                    user_chip INTEGER,
                    used_pin_number INTEGER,
                    online_order INTEGER,
                    fraud INTEGER);"""
            try:
                cursor.execute(query)
                cnx.commit()
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("test_table already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
            if table == "ccf_data_full":
                insert_data_query = """LOAD DATA INFILE '/Users/pierresarzier/Credit_Card_Fraud/sources/dataset_csv/card_transdata.csv'
                                        INTO TABLE ccf_data.ccf_data_full
                                        FIELDS TERMINATED BY ','
                                        ENCLOSED BY '"'
                                        LINES TERMINATED BY '\r'
                                        IGNORE 1 ROWS;"""
            elif table == 'ccf_data_partial':
                insert_data_query = """INSERT INTO ccf_data.ccf_data_partial SELECT * FROM ccf_data.ccf_data_full LIMIT 1000;"""
            elif table == "ccf_data_i":
                insert_data_query = """INSERT INTO ccf_data.ccf_data_i SELECT * FROM ccf_data.ccf_data_partial;"""
            elif table == "ccf_data_remaining":
                insert_data_query = """INSERT INTO ccf_data.ccf_data_remaining SELECT * FROM ccf_data.ccf_data_full LIMIT 1000, 10000000;"""
            else :
                break
                #insert_data_query = """INSERT INTO ccf_data.ccf_data_to_add SELECT * FROM ccf_data.ccf_data_partial;"""
            try:

                cursor.execute(insert_data_query)
                cnx.commit()
                print("data added to database")
            except mysql.connector.Error as err:
                print("Data insertion to test_table failed \n", table, err)
        cursor.close()
        cnx.close()

        testconfig ={
                'host': MYSQL_HOST,
                'user': MYSQL_USER,
                'password': MYSQL_PASSWORD,
                'database': MYSQL_DB
            }
        cls.mock_db_config = patch.dict(db_utils_data.config, testconfig)

"""    @classmethod
    def tearDownClass(cls):
        cnx = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = cnx.cursor(dictionary=True)

        # drop test database
        try:
            cursor.execute("DROP DATABASE {}".format(MYSQL_DB))
            cnx.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print("Database {} does not exists. Dropping db failed".format(MYSQL_DB))
        cnx.close()"""