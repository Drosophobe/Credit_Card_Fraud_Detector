from pydantic import BaseModel
from typing import List, Optional
import pickle 
from fastapi import  HTTPException, status
from enum import Enum, IntEnum
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI
import json
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 
from passlib.hash import bcrypt
import jwt
####################################################### AUTHENTICATION ##########################################################

app = FastAPI(openapi_tags=[{'name': 'prediction', 'description': 'prediction of credit card fraud'}])
JWT_SECRET = 'LePlombPaletteSurLeRhône'
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique =True)
    password_hash = fields.CharField(128)

    """@classmethod
    async def get_user(cls, username):
        return cls.get(username=username)"""

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)
User_Pydantic = pydantic_model_creator(User, name = 'User')
UserIn_Pydantic = pydantic_model_creator(User, name ='UserIn', exclude_readonly=True)
async def authenticate_user(username: str, password:str):
    user=await User.get(username= username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')
@app.post('/token')
async def generate_token(form_data:OAuth2PasswordRequestForm = Depends()):
    user=await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Invalid username or password')
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return {'access_token': token, 'token_type': 'bearer'}
async def get_current_user(token : str=Depends(oauth2_scheme)):
    try: 
        payload = jwt.decode(token, JWT_SECRET, algorithms = ['HS256'])
        user = await User.get(id= payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Invalid username or password')
    return await User_Pydantic.from_tortoise_orm(user)
@app.post('/users', response_model=User_Pydantic)
async def create_user(user: User_Pydantic):
    user_obj = User(username=user.username, password_hash = bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)
@app.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic= Depends(get_current_user)):
    return user
register_tortoise(app, db_url = 'sqlite://db.sqlite3', modules={'models': ['main']}, generate_schemas=True, add_exception_handlers=True)


"""async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}"""
####################################################### MODEL ##########################################################
def load_model(used_model = "dt_full"):
    """
    Load the model from pickle
    Default is full model
    It will be updated to parital later
    """
    loaded_model = pickle.load(open(f"{used_model}.sav", 'rb'))
    return loaded_model 
test = pd.DataFrame([[4.158589,0.079312,8.314564,1,0,0,1]])
print(load_model().predict(test))

# Base model Creation in order to specify the type of each variables 
class FeaturesBase(BaseModel):
    """
    Use this BaseModel to pass the features of the transaction 
    """
    distance_from_home : float
    distance_from_last_transaction : float
    ratio_to_median_purchase_price : float
    repeat_retailer : int
    used_chip : int
    used_pin_number : int
    online_order : int
    
####################################################### PREDICTION ROUTE ##########################################################
@app.post('/transaction', name='Prediction', tags=['prediction'])
async def create_transaction(data: FeaturesBase, custom_header: Optional[str] = Header(None, description='Remarks : '), token: str = Depends (oauth2_scheme)):
    """
    This function send back the prediction of our transaction 
    \n 0 => Ham
    \n 1 => Spam 
    """
    new_data = [[data.distance_from_home, data.distance_from_last_transaction, data.ratio_to_median_purchase_price,
    data.repeat_retailer, data.used_chip, data.used_pin_number, data.online_order]]
    output = load_model().predict(new_data)[0]
    if output == 1:
            prediction = "It's a Spam"
    else :
            prediction = "It's an Ham"
    return {'header': custom_header,
        'prediction :': prediction }
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port =8000)


class ModelLanguage(str, Enum):
    fr = "fr"
    en = "en"

