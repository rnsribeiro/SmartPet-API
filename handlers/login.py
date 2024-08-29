from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Função que verifica as credenciais do usuário
def authenticate_user(username: str, password: str):
    # Implementar lógica de autenticação, como verificar o banco de dados
    # Por simplicidade, vamos supor que o username é "user" e a senha é "password"
    if username == "user" and password == "password":
        return {"username": username}
    return None

# Função que gera o token (aqui apenas um exemplo simples)
def create_access_token(username: str):
    return f"token-for-{username}"


