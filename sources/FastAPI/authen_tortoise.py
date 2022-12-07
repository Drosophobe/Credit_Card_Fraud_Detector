
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 
from passlib.hash import bcrypt
from datetime import datetime, timedelta
import jwt
app = FastAPI()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
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
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
@app.post('/token')
async def generate_token(form_data:OAuth2PasswordRequestForm = Depends()):
    user=await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Invalid username or password')
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    access_token = jwt.encode(user_obj.dict(), SECRET_KEY)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
async def get_current_user(access_token : str=Depends(oauth2_scheme)):
    try: 
        payload = jwt.decode(access_token, SECRET_KEY, algorithms = ['HS256'])
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
register_tortoise(app, db_url = 'sqlite://db.sqlite3', modules={'models': ['authen_tortoise']}, generate_schemas=True, add_exception_handlers=True)

