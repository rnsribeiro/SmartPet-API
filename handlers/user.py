from fastapi import HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet  # Substitua 'mydatabase' pelo nome do seu banco de dados
users_collection = db.users  # Substitua 'users' pelo nome da coleção que você deseja usar

# Modelo para a criação de um novo usuário
class UserCreate(BaseModel):
    username: str
    name: str
    email: str
    password: str

# Modelo para a resposta da API com o ID e informações do usuário
class User(BaseModel):
    id: str  # Usaremos o ID do MongoDB como uma string
    username: str
    name: str
    email: str

# Handler para criar um novo usuário
def create_user(user: UserCreate):
    # Verifica se o username ou email já existem
    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        if existing_user.get("username") == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_user.get("email") == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Criptografa a senha
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Insere o novo usuário na base de dados
    new_user = {
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "password": hashed_password.decode('utf-8')  # Armazena a senha criptografada
    }
    result = users_collection.insert_one(new_user)
    # Retorna o usuário criado, incluindo o ID gerado pelo MongoDB
    return User(id=str(result.inserted_id), username=user.username, name=user.name, email=user.email)

# Handler para ler os dados de um usuário específico
def read_user(user_id: str):
    # Converte o ID para ObjectId
    obj_id = ObjectId(user_id)
    user = users_collection.find_one({"_id": obj_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Retorna o usuário encontrado (não retorna a senha)
    return User(id=str(user["_id"]), username=user["username"], name=user["name"], email=user["email"])

# Handler para listar todos os usuários
def list_users():
    users = []
    for user in users_collection.find():
        users.append(User(id=str(user["_id"]), username=user["username"], name=user["name"], email=user["email"]))
    return users
