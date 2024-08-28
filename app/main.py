from fastapi import FastAPI
from handlers.user import create_user, read_user, list_users
from handlers.dispenser import create_dispenser, update_level_water, update_level_feed, update_levels, list_dispensers, get_level_water, get_level_feed, get_levels

app = FastAPI()

# Definição das rotas de usuário
app.post("/user/")(create_user)
app.get("/user/{user_id}")(read_user)
app.get("/user/")(list_users)

# Definição das rotas referentes ao dispenser
app.post("/dispenser/")(create_dispenser)
app.post("/dispenser/water/{dispenser_id}")(update_level_water)
app.post("/dispenser/feed/{dispenser_id}")(update_level_feed)
app.post("/dispenser/levels/{dispenser_id}")(update_levels)
app.get("/dispenser/")(list_dispensers)
app.get("/dispenser/water/{dispenser_id}")(get_level_water)
app.get("/dispenser/feed/{dispenser_id}")(get_level_feed)
app.get("/dispenser/levels/{dispenser_id}")(get_levels)