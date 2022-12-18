import pickle
import pandas as pd

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
