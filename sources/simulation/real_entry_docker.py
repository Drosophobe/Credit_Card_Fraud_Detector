import requests
import random
import pandas as pd
import mysql.connector 
from mysql.connector import Error
from sqlalchemy import create_engine
# ast library is used to convert string from response.text to a dictionary in order to extract the token of the user created in the token section
import ast
API_HOST = "0.0.0.0"
API_PORT = "8000"
MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "ccf_mysql"
MYSQL_TABLE = "user"
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ',
    'Content-Type': 'application/json',}
def load_data_from_db(table_name):
    sqlEngine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}")
    dbConnection = sqlEngine.connect()
    df = pd.read_sql(f"SELECT * FROM {MYSQL_DB}.{table_name}", dbConnection)
    return df
print("dagobert")
df = load_data_from_db("ccf_data_remaining")
def load_entry_from_df(x_1, x_2, x_3, x_4, x_5, x_6, x_7, headers= headers):
    headers = headers
    json_data = {
    'distance_from_home': x_1,
    'distance_from_last_transaction': x_2,
    'ratio_to_median_purchase_price': x_3,
    'repeat_retailer': x_4,
    'used_chip': x_5,
    'used_pin_number': x_6,
    'online_order': x_7,}
    response = requests.post(f'http://{API_HOST}:{API_PORT}/model/predict/vi', headers=headers, json=json_data)
    print(response.json())
    return response.json()["Model vi : \n fraud ?"]
def load_entry_from_rdm(headers):
    headers = headers
    json_data = {
    'distance_from_home': random.uniform(0, 11000),
    'distance_from_last_transaction': random.uniform(0, 12000),
    'ratio_to_median_purchase_price': random.uniform(0, 270),
    'repeat_retailer': random.randint(0, 1),
    'used_chip': random.randint(0, 1),
    'used_pin_number': random.randint(0, 1),
    'online_order': random.randint(0, 1),}
    response = requests.post(f'http://{API_HOST}:{API_PORT}/model/predict/vi', headers=headers, json=json_data)
    print(response.json())
    return response.json()["Model vi : \n fraud ?"]
for i, j in df.iterrows():
    print(j)
    print(i)
    """if i % 2:
        load_entry_from_df(j["distance_from_home"], j["distance_from_last_transaction"], j["ratio_to_median_purchase_price"], int(j["repeat_retailer"]), int(j["used_chip"]), int(j["used_pin_number"]), int(j["online_order"]))
    else : 
        load_entry_from_rdm(headers = headers)"""
    load_entry_from_df(j["distance_from_home"], j["distance_from_last_transaction"], j["ratio_to_median_purchase_price"], int(j["repeat_retailer"]), int(j["used_chip"]), int(j["used_pin_number"]), int(j["online_order"]))
    if i == 5000:
        break