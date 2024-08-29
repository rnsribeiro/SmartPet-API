from fastapi import FastAPI, Depends
from handlers.user import create_user, read_user, list_users
from handlers.auth import login_for_access_token, get_current_user

app = FastAPI()

# Rota de login
app.post("/token")(login_for_access_token)

# Rotas protegidas
app.post("/user/")(create_user)
app.get("/user/{user_id}")(read_user)
app.get("/user/")(list_users)
