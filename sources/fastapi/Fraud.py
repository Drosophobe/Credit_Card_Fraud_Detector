import pickle
import pandas as pd

# Load model
loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
scaler=pickle.load(open("scaler.pkl", 'rb'))

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


def Fraud(Input_list):
    Fraud_eval=pd.DataFrame([Input_list],columns=['distance_from_home',
                               'distance_from_last_transaction',
                               'ratio_to_median_purchase_price',
                               'repeat_retailer',
                               'used_chip',
                               'used_pin_number',
                               'online_order'])
    result=loaded_model.predict(scaler.transform(Fraud_eval)) 
    if result[0]==0:
        return ("No Fraud")
    else:
        return ("Fraud")