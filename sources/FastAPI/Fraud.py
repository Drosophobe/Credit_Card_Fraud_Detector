import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
# Load models
loaded_model_partial = pickle.load(open('../models/dt_partial.sav', 'rb'))
loaded_model_i = pickle.load(open('../models/dt_i.sav', 'rb'))
loaded_model_full = pickle.load(open('../models/dt_full.sav', 'rb'))
#scaler=pickle.load(open("scaler.pkl", 'rb'))

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
def Retrain():
    df = pd.read_csv("../Datasets/df_i.csv", index_col = 0)
    model_i = DecisionTreeClassifier(max_depth = 8, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(df.drop(['fraud'],axis = 1), df['fraud'], random_state=42)
    model_i.fit(X_train, y_train)
    filename = '../models/dt_i.sav'
    pickle.dump(model_i, open(filename, 'wb'))

Retrain()