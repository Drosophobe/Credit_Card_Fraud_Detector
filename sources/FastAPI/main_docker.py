from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Libraries used for html templates (Above)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from fastapi.responses import HTMLResponse
# pip install passlib to get hashed password
from passlib.hash import bcrypt
# pip install pyjwt
import jwt
from typing import Optional
import pandas as pd
from Fraud import *
df_i = pd.DataFrame(columns=["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "user_chip", "used_pin_number", "online_order", "fraud"])
app = FastAPI()
# Load templates and static contents
#app.mount("/static", StaticFiles(directory="static"), name="static")
#templates = Jinja2Templates(directory="templates")
JWT_SECRET = '2DD282EDA4F33BCF5FAD1C9F6F75069F1FCE13102BB56393C4819B4EB48C0A40'
# Generated from https://www.grc.com/passwords.htm
ALGORITHM = 'HS256'
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    """@classmethod
    async def get_user(cls, username):
        return cls.get(username=username)"""
    # verify is the passwors is correct
    def verify_password(self, password):
        # On vérifie que le password hashed est bien le password après décryption
        return bcrypt.verify(password, self.password_hash)
        
# infos of the user
User_Pydantic = pydantic_model_creator(User, name='User')
# Infos the user pass in the api 
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
ouath2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')
async def authenticate_user(username:str, password:str):
    user = await User.get(username = username)
    if not user:
        return False
    if not user.verify_password(password): 
        return False
    return user
@app.post('/token')
# On crée une fonction qui génére un token en dépandant de l'authentificaiton 
async def generate_token(form_data: OAuth2PasswordRequestForm= Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details = 'Invalid username or password')
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET, ALGORITHM)
    return {'access_token': token, 'token_type': 'bearer'}
async def get_current_user(token: str = Depends(ouath2_scheme)):
    try:
        payload = jwt.decode( token, JWT_SECRET, ALGORITHM)
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details = 'Invalid username or password')
    return await User_Pydantic.from_tortoise_orm(user)
@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    # permet de mettre dans la db l'username et le password hashed du nouvel user
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    # On attends que l'user_obj est bien save dans la db
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)
@app.get('/users/me', response_model = User_Pydantic)
async def get_user(user:User_Pydantic = Depends(get_current_user)):
        return user

#########################################PREDICTIONS####################################################
path = 'Datasets/'
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
@app.post('/model/predict/v0', name="Predict Credit Card Fraud", tags=['users'])
def post_predict( new_request: Data, username: str = Depends(get_current_user) ):
    '''
    Use model_partial to predict fraud, output = 'Fraud' or 'No Fraud'
    '''
    input_list = [item[1] for item in new_request]
    response = Fraud(input_list, loaded_model_partial)
    return {'Model v0 : \n fraud ?': response}

@app.post('/model/predict/vi', name="Predict Credit Card Fraud and store datas", tags=['users'])
def post_predict(new_request: Data, username: str = Depends(get_current_user)):
    '''
    Use model_in_progress to predict fraud, output = 'Fraud' or 'No Fraud'
    '''
    series_list = [item[1] for item in new_request]
    response = Fraud(series_list, loaded_model_partial)
    print(series_list)
    # Vérifier si la prediction vient de la db ou non
    if response=='Fraud':
        x=1
    else:
        x=0
    # We are goining to check if the pred asked come from ccf_data_remaining or a new input
    # If yes we will save the 'fraud' from db not pred if not we will save the prediction
    in_db = check_if_prediction_in_db(series_list)
    if in_db[0] :
        x = in_db[1]
        origin = "Corrected"
    else:
        origin = "Not Corrected"
    global df_i
    series_list.append(x)
    serie_i = pd.Series(series_list, index = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price", "repeat_retailer", "user_chip", "used_pin_number", "online_order", "fraud"])
    df_i = df_i.append(serie_i, ignore_index = True)
    print(df_i)
    save_prediction_to_db(serie_i)
    return {'Model vi : \n fraud ?': response, "Origin :": origin} 
@app.post('/model/predict/v1', name="Predict Credit Card Fraud", tags=['users'])
def post_predict( new_request: Data, username: str = Depends(get_current_user) ):
    '''
    Use model_final to predict fraud, output = 'Fraud' or 'No Fraud'
    '''
    input_list = [item[1] for item in new_request]
    response = Fraud(input_list, loaded_model_full)
    return {'Model v1 : \n fraud ?': response}

@app.post('/model/save', name="Update database from previous predicitons", tags=['users'])
def post_save(username: str = Depends(ouath2_scheme) ):
    '''Use model to predict fraud, save result to database, output = database tail
    '''
    # Tout ça est à refaire avec les databases
    if username == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ":
        insert_prediction_to_db()
        #df_0 = pd.read_csv("../Datasets/df_partial.csv", index_col = 0)
        #df_2 = pd.concat([df_0, df_i], ignore_index=True)
        #df_2.to_csv("../Datasets/df_i.csv")
        return "The Database has been successfully updated"
    else:
        return "Please sign in as the admin to do such thing"
@app.post('/model/train_model', name = "Retrain the model based on database previous update")
def post_retrain(username: User_Pydantic = Depends(ouath2_scheme)):
    if username == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ":
        Retrain()
        return "The model has been updated"
    else :
        return "Please sign in as the admin to do such thing"
# Pour la db en mySQL il faut lancer un server puis télécharger MySQLWorkBench et aller dans l'onget Database -> Manage connection -> New - > set le name à ccf_users et changer l'ip et le port en fonction de tes entrées (par defaut le mdp est à rien) 
register_tortoise(app, db_url ='mysql://root:Daniel@mysql:3306/ccf_mysql', modules={'models': ['main']}, generate_schemas = True, add_exception_handlers = True)