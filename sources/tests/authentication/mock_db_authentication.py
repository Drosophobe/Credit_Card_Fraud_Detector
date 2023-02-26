import mysql.connector
from mysql.connector import errorcode
from unittest import TestCase
from mock import patch
import db_utils_authentication

MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Daniel"
MYSQL_DB = "ccf_mysql"
MYSQL_TABLE = "user"
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
            cursor.execute(f"DROP TABLE {MYSQL_DB}.{MYSQL_TABLE}")
            cursor.close()
            print("DB dropped")
        except mysql.connector.Error as err:
            print("{}{}".format(MYSQL_DB, err))

        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(MYSQL_TABLE))
            print("DB Created")
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)
        cnx.database = MYSQL_TABLE

        query = """CREATE TABLE ccf_mysql.user (
                  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY ,
                  `username` varchar(50) NOT NULL,
                  `password_hash` varchar(128) NOT NULL,
                  UNIQUE(username)
                )"""
        try:
            cursor.execute(query)
            cnx.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("test_table already exists.")
            else:
                print(err.msg)
        else:
            print("Table user created")

        insert_data_query = """INSERT INTO ccf_mysql.user (`id`, `username`, `password_hash`) VALUES
                            ('1', 'admin', '$2b$12$.JtAneBODWfF29sdJbCgceK8UKjISRSki3vHRIP7OMyk.xsTO49NG')"""
        try:
            cursor.execute(insert_data_query)
            cnx.commit()
            print("data added to database")
        except mysql.connector.Error as err:
            print("Data insertion to test_table failed \n" + err)
        cursor.close()
        cnx.close()

        testconfig ={
            'host': MYSQL_HOST,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'database': MYSQL_TABLE
        }
        cls.mock_db_config = patch.dict(db_utils_authentication.config, testconfig)

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
