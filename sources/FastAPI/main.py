from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
# pip install passlib to get hashed password
from passlib.hash import bcrypt
# pip install pyjwt
import jwt
app = FastAPI()
JWT_SECRET = 'my_secret'
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

#########################################AJOUTER MODEL ICI####################################################

# Pour la db en mySQL il faut lancer un server puis télécharger MySQLWorkBench et aller dans l'onget Database -> Manage connection -> New - > set le name à ccf_users et changer l'ip et le port en fonction de tes entrées (par defaut le mdp est à rien) 
register_tortoise(app, db_url ='mysql://root:@127.0.0.1:3306/ccf_users', modules={'models': ['main']}, generate_schemas = True, add_exception_handlers = True)