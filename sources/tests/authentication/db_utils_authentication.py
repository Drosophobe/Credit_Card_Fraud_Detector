import mysql.connector
from mysql.connector import errorcode
import MySQLdb
MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Daniel"
MYSQL_DB = "ccf_mysql"
MYSQL_TABLE = "user"
MYSQL_PORT = "3306"
config = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DB
}

def db_read(query, params=None):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        entries = cursor.fetchall()
        cursor.close()
        cnx.close()

        content = []

        for entry in entries:
            content.append(entry)

        return content

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("User authorization error")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database doesn't exist")
        else:
            print(err)
    else:
        cnx.close()
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
            print("Connection closed")
       
def db_write(query, params=None):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            cnx.commit()
            cursor.close()
            cnx.close()
            return True

        except MySQLdb._exceptions.IntegrityError:
            cursor.close()
            cnx.close()
            return False

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("User authorization error")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database doesn't exist")
        else:
            print(err)
        return False
    else:
        cnx.close()
        return False
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
            print("Connection closed")
