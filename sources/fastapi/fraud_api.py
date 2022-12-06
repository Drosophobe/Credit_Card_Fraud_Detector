# ======================================================================
# Credit Card Fraud Detection API
# v 1.0.1
# P. Sarzier, P.Hutter
# Datascientest MLOps Oct. 2022
# ======================================================================

import pandas as pd 
import json

from fastapi import Response
from fastapi.responses import HTMLResponse

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException


# import from config file
from config import users_db, path

# import doc file
from doc import doc


from Fraud import Fraud


# Lanch of fastAPI
api = FastAPI(
    title="fraud_API",
    description="Datascientest MLOps project API powered by FastAPI.",
    version="1.0.1"
)

# Baisc Auth. 
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    is_authorized = (credentials.username in users_db.keys()) and (credentials.password==users_db.get(credentials.username))
    
    if not is_authorized:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Welcome page
@api.get('/', response_class=HTMLResponse, name='Welcome page', tags=['all'])
def get_usage():
    """Welcome page, output = list of API commands / user profile
    """
    return doc

# Change password
@api.get('/users/pw', name="Change password", tags=['users'])
def get_pw(new_pw: str, username: str = Depends(get_current_username) ):
    '''Change current password with a new password, output= {username, password}
    ''' 
    if new_pw == '':
        raise HTTPException(
            status_code=401,
            detail="No password",
        )
    
    users_db[username]=new_pw
    with open(path+'users.json', 'w') as f:
        json.dump(users_db, f)
    f.close()
    return {"username":username, "password":new_pw}

# Predict fraud

# Define Data structure
from typing import Optional
from pydantic import BaseModel

class Data(BaseModel):
    """Data Record fields description
    """
    distance_from_home: float
    distance_from_last_transaction: float
    ratio_to_median_purchase_price: float
    repeat_retailer: int
    used_chip: int
    used_pin_number: int
    online_order: Optional[int]
    

@api.post('/users/predict', name="Predict Credit Card Fraud", tags=['users'])
def post_predict( new_request: Data, username: str = Depends(get_current_username) ):
    '''Use model to predict fraud, output = 'Fraud' or 'No Fraud'
    '''
    input_list = [item[1] for item in new_request]
    response = Fraud(input_list)
    return {'fraud ?': response} 

@api.post('/users/save', name="Predict Credit Card Fraud and update database", tags=['users'])
def post_predict_save( new_request: Data, username: str = Depends(get_current_username) ):
    '''Use model to predict fraud, save result to database, output = database tail
    '''
    input_list = [item[1] for item in new_request]
    response = Fraud(input_list)
    if response=='Fraud':
        x=1
    else:
        x=0
    # save in database
    df = pd.read_csv(path+"card_transdata.csv")
    input_list.append(x)
    df_new_line=pd.DataFrame(data=input_list).T
    df_new_line.columns = df.columns
    df=pd.concat([df, df_new_line], axis=0).reset_index(drop=True)
    # update question.csv
    #df.to_csv(path+"card_transdata.csv", encoding='utf-8', index=False)
    return HTMLResponse(content=df.tail().to_html(), status_code=200)
    #return {"output": input_list}

# Add new user access to Fraud API

class Users(BaseModel):
    """Users_db Record fields description
    """
    name: str
    password: str

@api.post('/admin', name="Add new user", tags=['admin'])
def post_new( new_user: Users, username: str = Depends(get_current_username) ):
    '''Admin dedicated page for new user creation, output = new list of users and password
    '''
    if username!='admin':
        raise HTTPException(
            status_code=401,
            detail="Only Admin access",
            headers={"WWW-Authenticate": "Basic"}
        )
    if new_user.name in users_db.keys():
        raise HTTPException(
            status_code=401,
            detail="Username still exists",
        )
    if (new_user.name == '') or (new_user.password == ''):
        raise HTTPException(
            status_code=401,
            detail="No username or no password",
        )
    users_db[new_user.name]=new_user.password
    with open(path+'users.json', 'w') as f:
        json.dump(users_db, f)
    f.close()
    return {"users_db": users_db}

@api.delete('/admin', name="Suppress user", tags=['admin'])
def delete_user( user: str, username: str = Depends(get_current_username) ):
    '''Admin dedicated page for suppress user , output = new list of users and password
    '''
    if username!='admin':
        raise HTTPException(
            status_code=401,
            detail="Only Admin access",
            headers={"WWW-Authenticate": "Basic"}
        )
    if user not in users_db.keys():
        raise HTTPException(
            status_code=401,
            detail="Username not exists",
        )
    if user == '':
        raise HTTPException(
            status_code=401,
            detail="Username empty",
        )
    del users_db[user]
    with open(path+'users.json', 'w') as f:
        json.dump(users_db, f)
    f.close()
    return {"users_db": users_db}

    # End of API