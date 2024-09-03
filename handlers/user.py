from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from handlers.auth import get_current_user, is_admin_user

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
users_collection = db.users

# Modelo para a criação de um novo usuário
class UserCreate(BaseModel):
    username: str
    name: str
    email: str
    password: str

# Modelo para a resposta da API com o ID e informações do usuário
class User(BaseModel):
    id: str
    username: str
    name: str
    email: str
    is_admin: bool

# Handler para criar um novo usuário
def create_user(user: UserCreate):
    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        if existing_user.get("username") == user.username:
            raise HTTPException(status_code=400, detail="Username or Email already registered")
        if existing_user.get("email") == user.email:
            raise HTTPException(status_code=400, detail="Username or Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = {
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "password": hashed_password.decode('utf-8'),
        "is_admin": False  # Sempre criado como False
    }
    result = users_collection.insert_one(new_user)
    return User(
        id=str(result.inserted_id),
        username=user.username,
        name=user.name,
        email=user.email,
        is_admin=new_user["is_admin"],
    )

# Handler para ler os dados de um usuário específico
def read_user(user_id: str, current_user: dict = Depends(get_current_user)):
    obj_id = ObjectId(user_id)
    user = users_collection.find_one({"_id": obj_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        id=str(user["_id"]),
        username=user["username"],
        name=user["name"],
        email=user["email"],
        is_admin=user.get("is_admin", False),
    )

# Handler para listar todos os usuários (apenas para admin)
def list_users(current_user: dict = Depends(is_admin_user)):
    users = []
    for user in users_collection.find():
        users.append(
            User(
                id=str(user["_id"]),
                username=user["username"],
                name=user["name"],
                email=user["email"],
                is_admin=user.get("is_admin", False),
            )
        )
    return users
