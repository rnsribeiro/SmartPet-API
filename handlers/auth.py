from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt

# Configurações do JWT
SECRET_KEY = "your-secret-key"  # Troque isso por uma chave secreta segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
users_collection = db.users

# Modelo para o Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Modelo para os dados contidos no Token
class TokenData(BaseModel):
    username: str | None = None

# Função para criar um token de acesso
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Função para verificar um usuário
def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return False
    return user

# Rota para fazer login e obter o token
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Função para obter o usuário atual baseado no token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = users_collection.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user
