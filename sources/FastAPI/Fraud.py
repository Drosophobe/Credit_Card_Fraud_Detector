import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import mysql.connector 
from mysql.connector import Error
from sklearn.metrics import f1_score
from sqlalchemy import create_engine
MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "ccf_mysql"
MYSQL_TABLE = "user"
MYSQL_PORT = "3306"
# Load models

loaded_model_partial = pickle.load(open('models/dt_partial.sav', 'rb'))
loaded_model_i = pickle.load(open('models/dt_i.sav', 'rb'))
loaded_model_full = pickle.load(open('models/dt_full.sav', 'rb'))
#scaler=pickle.load(open("scaler.pkl", 'rb'))
def load_data_from_db_2(table_name):
    try:
        connection = mysql.connector.connect(host=MYSQL_HOST, database = MYSQL_DB, user = MYSQL_USER, password = MYSQL_PASSWORD, autocommit=True)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            df = pd.read_sql('SELECT * FROM {}'.format(table_name), con=connection)
            return df
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
def load_data_from_db(table_name):
    sqlEngine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, pw=MYSQL_PASSWORD))
    dbConnection = sqlEngine.connect()
    df = pd.read_sql(f"SELECT * FROM {MYSQL_DB}.{table_name}", dbConnection)
    return df
def insert_prediction_to_db(db_name="ccf_mysql", table_name="ccf_data_i", ):
    try :
        connection = mysql.connector.connect(host=MYSQL_HOST, database = MYSQL_DB, user = MYSQL_USER, password = MYSQL_PASSWORD, autocommit=True)
        mySql_Insert_Table_Query = f"""INSERT INTO {db_name}.{table_name} SELECT * FROM ccf_mysql.ccf_data_to_add;  """
        cursor = connection.cursor()
        result_1 = cursor.execute(mySql_Insert_Table_Query)
        print("table : ccf_data_i successfully updated")
        # We Will remove values from data_remaining table to avoid duplicated values 
        mySQL_Remove_Values_Query = f"""DELETE  FROM ccf_data_remaining WHERE ROUND(distance_from_home, 4) IN (SELECT ROUND(distance_from_home, 4) FROM ccf_data_to_add) AND ROUND(distance_from_last_transaction, 4) IN 
(SELECT ROUND(distance_from_last_transaction, 4) FROM ccf_data_to_add) AND ROUND(ratio_to_median_purchase_price, 4) IN (SELECT ROUND(ratio_to_median_purchase_price, 4) FROM 
ccf_data_to_add);"""
        result_4 = cursor.execute(mySQL_Remove_Values_Query)
        print("table : ccf_data_remaining successfully updated")
        # Then we can discard predictions from ccf_data_to_add
        mySql_Delete_Table_Query = f"""DELETE FROM {db_name}.ccf_data_to_add;"""
        result_3 = cursor.execute(mySql_Delete_Table_Query)
        print("table : ccf_data_to_add successfully pruned")
        connection.commit()
        print(connection.autocommit)
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
def save_prediction_to_db(values, db_name = MYSQL_DB, table_name="ccf_data_to_add"):
    try :
        connection = mysql.connector.connect(host=MYSQL_HOST, database = MYSQL_DB, user = MYSQL_USER , password = MYSQL_PASSWORD, autocommit=True)
        if connection.is_connected():
            mySql_Create_Table_Query = f"""INSERT INTO {db_name}.{table_name} (distance_from_home, distance_from_last_transaction, ratio_to_median_purchase_price, repeat_retailer, used_chip, used_pin_number, online_order, fraud ) VALUES ({float(values["distance_from_home"])}, {float(values["distance_from_last_transaction"])}, {float(values["ratio_to_median_purchase_price"])}, {int(values["repeat_retailer"])}, {int(values["used_chip"])}, {int(values["used_pin_number"])}, {int(values["online_order"])}, {int(values["fraud"])});  """
            cursor = connection.cursor()
            result = cursor.execute(mySql_Create_Table_Query)
            print("Value successfully added into Table")
            connection.commit()
            print(connection.autocommit)
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))
    finally:
        if connection.is_connected():
            #cursor.close()
            connection.close()
            print("MySQL connection is closed")
def correct_and_remove_values(df_r, df_a):
    df_1 = pd.merge(df_r,df_a, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    df_2 = pd.merge(df_a,df_r, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    df_changed = pd.DataFrame([], columns = ['distance_from_home', 'distance_from_last_transaction', 'ratio_to_median_purchase_price', 'repeat_retailer', 'used_chip', 'used_pin_number', "online_order", 'fraud'])
    df_to_del = pd.DataFrame([], columns = ['distance_from_home', 'distance_from_last_transaction', 'ratio_to_median_purchase_price', 'repeat_retailer', 'used_chip', 'used_pin_number', "online_order", 'fraud'])
    df_to_add_add = pd.DataFrame([], columns = ['distance_from_home', 'distance_from_last_transaction', 'ratio_to_median_purchase_price', 'repeat_retailer', 'used_chip', 'used_pin_number', "online_order", 'fraud'])
    for i in df_2.index:
        my_list = []
        my_list_to_del = []
        my_list_to_add_add = []
        x_1 = df_2.loc[i][0]
        x_2 = df_2.loc[i][1]
        x_3 = df_2.loc[i][2]
        x_4 = df_2.loc[i][3] 
        x_5 = df_2.loc[i][4]
        x_6 = df_2.loc[i][5]
        x_7 = df_2.loc[i][6]
        x_8 = df_2.loc[i][7]
        df_bool = df_r[(df_r['distance_from_home']==x_1) & (df_r['distance_from_last_transaction']==x_2)& (df_r['ratio_to_median_purchase_price']==x_3)]
        my_list_to_del.extend([x_1, x_2, x_3, x_4, x_5, x_6, x_7, x_8])
        if df_bool.empty:
            my_list_to_add_add.extend([x_1, x_2, x_3, x_4, x_5, x_6, x_7, x_8])
        else:
            my_list.extend([x_1, x_2, x_3, x_4, x_5, x_6, x_7])
            my_list_to_add_add.extend([x_1, x_2, x_3, x_4, x_5, x_6, x_7])

            if x_8 == 0:
                my_list.append(1)
                my_list_to_add_add.append(1)
            else:
                my_list.append(0)
                my_list_to_add_add.append(0)
            df_changed = df_changed.append(pd.DataFrame([my_list], columns=df_changed.columns), ignore_index=True)
        df_to_add_add = df_to_add_add.append(pd.DataFrame([my_list_to_add_add], columns=df_to_add_add.columns), ignore_index=True)
        df_to_del = df_to_del.append(pd.DataFrame([my_list_to_del], columns=df_to_del.columns), ignore_index=True)
    df_3 = pd.merge(df_1,df_changed, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    df_3 = df_3.reset_index(drop = True)
    df_to_add = pd.merge(df_a, df_to_del, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    df_to_add = df_to_add.append(df_to_add_add)
    df_to_add = df_to_add.reset_index(drop = True)
    print("df_remaining_old : ", df_r.shape[0])
    print("df_remaining_new : ", df_3.shape[0])
    return df_3, df_to_add
def delete_and_save_db(df, MYSQL_HOST, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD, MYSQL_TABLE):
    hostname=MYSQL_HOST
    dbname=MYSQL_DB
    uname=MYSQL_USER
    pwd=MYSQL_PASSWORD

    # Delete TABLE
    connection = mysql.connector.connect(host=MYSQL_HOST, database = MYSQL_DB, user = MYSQL_USER, password = MYSQL_PASSWORD,autocommit=True)
    ####### end of connection ####
    my_cursor = connection.cursor()
    try:
        my_cursor.execute(f"DROP table  {MYSQL_TABLE}")
    except mysql.connector.Error as my_error:
        print(my_error)
    else:
        print(f"Table {MYSQL_TABLE} deleted ")

    # Create SQLAlchemy engine to connect to MySQL Database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))

    # Convert dataframe to sql table                                   
    df.to_sql(MYSQL_TABLE, engine, index=False)
    print(f"Table {MYSQL_TABLE} created ")
    if MYSQL_TABLE == "ccf_data_i":
        connection = mysql.connector.connect(host=MYSQL_HOST, database = MYSQL_DB, user = MYSQL_USER, password = MYSQL_PASSWORD,autocommit=True)
        ####### end of connection ####
        my_cursor = connection.cursor()
        try:
            my_cursor.execute("DROP table ccf_data_to_add")
            df_x = pd.DataFrame([], columns = ['distance_from_home', 'distance_from_last_transaction', 'ratio_to_median_purchase_price', 'repeat_retailer', 'used_chip', 'used_pin_number', "online_order", 'fraud'])
            df_x.to_sql("ccf_data_to_add", engine, index=False)
        except mysql.connector.Error as my_error:
            print(my_error)
        else:
            print("Table ccf_data_to_add deleted ")
def check_if_prediction_in_db(values):
    """
    This function return True if the prediction is in the db and False if not.
    We will use it to know when we have to update ccf_data_remaining table or not
    And also which value of target to use in the ccf_data_to_add table for retrain the model
    """
    df_remaining = load_data_from_db("ccf_data_remaining")
    df_values = pd.DataFrame(columns = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "used_chip", "used_pin_number", "online_order"])
    df_values = df_values.append(pd.Series(values, index = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "used_chip", "used_pin_number", "online_order"]), ignore_index=True)
    res = pd.merge(df_remaining, df_values, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    if df_remaining.shape[0] ==  res.shape[0]:
        return False , 
    else: 
        reality = df_remaining[(df_remaining["distance_from_home"].round(4) == df_values["distance_from_home"][0].round(4)) & (df_remaining["distance_from_last_transaction"].round(4) == df_values["distance_from_last_transaction"][0].round(4))&(df_remaining["ratio_to_median_purchase_price"].round(4) == df_values["ratio_to_median_purchase_price"][0].round(4))&(df_remaining["repeat_retailer"].round(4) == df_values["repeat_retailer"][0].round(4))&(df_remaining["used_chip"].round(4) == df_values["used_chip"][0].round(4))&(df_remaining["used_pin_number"].round(4) == df_values["used_pin_number"][0].round(4))&(df_remaining["online_order"].round(4) == df_values["online_order"][0].round(4))]["fraud"].iloc[0]
        return True, reality
def Fraud(Input_list, model= loaded_model_full):
    Fraud_eval=pd.DataFrame([Input_list],columns=['distance_from_home',
                               'distance_from_last_transaction',
                               'ratio_to_median_purchase_price',
                               'repeat_retailer',
                               'used_chip',
                               'used_pin_number',
                               'online_order'])
    result=model.predict(Fraud_eval)
    if result[0]==0:
        return ("No Fraud")
    else:
        return ("Fraud")
def Retrain(path = "models/"):

    df = load_data_from_db('ccf_data_i')
    model_i = DecisionTreeClassifier(max_depth = 8, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(df.drop(['fraud'],axis = 1), df['fraud'], random_state=42)
    #loaded_model_i.fit(X_train, y_train)
    print("previous score : ", f1_score(loaded_model_i.predict(X_test), y_test))
    model_i.fit(X_train, y_train)
    print("Current score : ",f1_score(model_i.predict(X_test), y_test))
    if f1_score(loaded_model_i.predict(X_test), y_test) < f1_score(model_i.predict(X_test), y_test):
        filename = path + 'dt_i.sav'
        pickle.dump(model_i, open(filename, 'wb'))
        print("New model succesfully updated")
    else :
        print("The old model was good enough")
