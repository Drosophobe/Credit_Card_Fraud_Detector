import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import mysql.connector 
from mysql.connector import Error
# Load models
loaded_model_partial = pickle.load(open('models/dt_partial.sav', 'rb'))
loaded_model_i = pickle.load(open('models/dt_i.sav', 'rb'))
loaded_model_full = pickle.load(open('models/dt_full.sav', 'rb'))
#scaler=pickle.load(open("scaler.pkl", 'rb'))
# You have to be located in sources/FastAPI
# Fraud function
'''
Returns 'Fraud' or 'No Fraud' with the following Inputs_list
['distance_from_home',
'distance_from_last_transaction',
'ratio_to_median_purchase_price',
'repeat_retailer',
'used_chip',
'used_pin_number',
'online_order'
'''
def load_data_from_db(table_name):
    try:
        connection = mysql.connector.connect(host='mysql', database = 'ccf_mysql', user = 'root', password = 'Daniel',autocommit=True)
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
def insert_prediction_to_db(db_name="ccf_data", table_name="ccf_data_i", ):
    try :
        connection = mysql.connector.connect(host='mysql', database = 'ccf_mysql', user = 'root', password = 'Daniel', autocommit=True)
        mySql_Insert_Table_Query = f"""INSERT INTO {db_name}.{table_name} SELECT * FROM ccf_data.ccf_data_to_add;  """
        cursor = connection.cursor()
        result_1 = cursor.execute(mySql_Insert_Table_Query)
        # We Will remove values from data_remaining table to avoid duplicated values 
        mySQL_Remove_Values_Query = f"""DELETE  FROM ccf_data_remaining WHERE ROUND(distance_from_home, 4) IN (SELECT ROUND(distance_from_home, 4) FROM ccf_data_to_add) AND ROUND(distance_from_last_transaction, 4) IN (SELECT ROUND(distance_from_last_transaction, 4) FROM ccf_data_to_add) AND ROUND(ratio_to_median_purchase_price, 4) IN (SELECT ROUND(ratio_to_median_purchase_price, 4) FROM ccf_data_to_add);"""
        result_4 = cursor.execute(mySQL_Remove_Values_Query)
        # Then we can discard predictions from ccf_data_to_add
        mySql_Delete_Table_Query = f"""DELETE FROM {db_name}.ccf_data_to_add;"""
        result_3 = cursor.execute(mySql_Delete_Table_Query)
        print("Update and Delete tables successfull")
        connection.commit()
        print(connection.autocommit)
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
def save_prediction_to_db(values, db_name = "ccf_mysql", table_name="ccf_data_to_add"):
    try :
        connection = mysql.connector.connect(host='mysql', database = db_name, user = 'root', password = 'Daniel', autocommit=True)
        if connection.is_connected():
            mySql_Create_Table_Query = f"""INSERT INTO {db_name}.{table_name} (distance_from_home, distance_from_last_transaction, ratio_to_median_purchase_price, repeat_retailer, user_chip, used_pin_number, online_order, fraud ) VALUES ({float(values["distance_from_home"])}, {float(values["distance_from_last_transaction"])}, {float(values["ratio_to_median_purchase_price"])}, {int(values["repeat_retailer"])}, {int(values["user_chip"])}, {int(values["used_pin_number"])}, {int(values["online_order"])}, {int(values["fraud"])});  """
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
def check_if_prediction_in_db(values):
    """
    This function return True if the prediction is in the db and False if not.
    We will use it to know when we have to update ccf_data_remaining table or not
    And also which value of target to use in the ccf_data_to_add table for retrain the model
    """
    df_remaining = load_data_from_db("ccf_data_remaining")
    df_values = pd.DataFrame(columns = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "user_chip", "used_pin_number", "online_order"])
    df_values = df_values.append(pd.Series(values, index = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "user_chip", "used_pin_number", "online_order"]), ignore_index=True)
    res = pd.merge(df_remaining, df_values, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    if df_remaining.shape[0] ==  res.shape[0]:
        return False , 
    else: 
        reality = df_remaining[(df_remaining["distance_from_home"].round(4) == df_values["distance_from_home"][0].round(4)) & (df_remaining["distance_from_last_transaction"].round(4) == df_values["distance_from_last_transaction"][0].round(4))&(df_remaining["ratio_to_median_purchase_price"].round(4) == df_values["ratio_to_median_purchase_price"][0].round(4))&(df_remaining["repeat_retailer"].round(4) == df_values["repeat_retailer"][0].round(4))&(df_remaining["user_chip"].round(4) == df_values["user_chip"][0].round(4))&(df_remaining["used_pin_number"].round(4) == df_values["used_pin_number"][0].round(4))&(df_remaining["online_order"].round(4) == df_values["online_order"][0].round(4))]["fraud"].iloc[0]
        return True, reality
def Fraud(Input_list, model= loaded_model_full):
    Fraud_eval=pd.DataFrame([Input_list],columns=['distance_from_home',
                               'distance_from_last_transaction',
                               'ratio_to_median_purchase_price',
                               'repeat_retailer',
                               'user_chip',
                               'used_pin_number',
                               'online_order'])
    result=model.predict(Fraud_eval)
    if result[0]==0:
        return ("No Fraud")
    else:
        return ("Fraud")
def Retrain(path = "../models/"):

    df = load_data_from_db('ccf_data_i')
    model_i = DecisionTreeClassifier(max_depth = 8, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(df.drop(['fraud'],axis = 1), df['fraud'], random_state=42)
    loaded_model_i.fit(X_train, y_train)
    print(loaded_model_i.score(X_test, y_test))
    model_i.fit(X_train, y_train)
    print(model_i.score(X_test, y_test))
    # Rajouter if score_i> score_init
    if loaded_model_i.score(X_test, y_test) < model_i.score(X_test, y_test):
        filename = path + 'dt_i.sav'
        pickle.dump(model_i, open(filename, 'wb'))
    else :
        print("The old model was good enough")

Retrain()