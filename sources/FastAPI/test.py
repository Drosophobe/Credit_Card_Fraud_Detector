import mysql.connector

connection = mysql.connector.connect(user='root', password='Daniel', host='mysql', port='3306', database 
='ccf_mysql')
print('COnnected')

cursor = connection.cursor()
cursor.execute("SELECT * FROM ccf_data_partial")
students =cursor.fetchall()
connection.close()
print(students)
