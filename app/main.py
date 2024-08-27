from fastapi import FastAPI
from handlers.user import create_user, read_user, list_users

app = FastAPI()

# Definição das rotas
app.post("/user/")(create_user)
app.get("/user/{user_id}")(read_user)
app.get("/user/")(list_users)
