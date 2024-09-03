from fastapi import FastAPI, Depends
from handlers.user import create_user, read_user, list_users
from handlers.dispenser import (
    create_dispenser,
    update_level_water,
    update_level_feed,
    update_levels,
    list_dispensers,
    get_level_water,
    get_level_feed,
    get_levels,
)
from handlers.auth import login_for_access_token, get_current_user
from handlers.pet import create_pet, read_pet, update_pet, delete_pet, list_pets

app = FastAPI()

# Rota de login
app.post("/token")(login_for_access_token)

# Rotas protegidas para usuários
app.post("/user/")(create_user)
app.get("/user/{user_id}", dependencies=[Depends(get_current_user)])(read_user)
app.get("/user/", dependencies=[Depends(get_current_user)])(list_users)

# Rotas protegidas para dispensers
app.post("/dispenser/", dependencies=[Depends(get_current_user)])(create_dispenser)
app.post("/dispenser/water/{dispenser_id}", dependencies=[Depends(get_current_user)])(update_level_water)
app.post("/dispenser/feed/{dispenser_id}", dependencies=[Depends(get_current_user)])(update_level_feed)
app.post("/dispenser/levels/{dispenser_id}", dependencies=[Depends(get_current_user)])(update_levels)
app.get("/dispenser/", dependencies=[Depends(get_current_user)])(list_dispensers)
app.get("/dispenser/water/{dispenser_id}", dependencies=[Depends(get_current_user)])(get_level_water)
app.get("/dispenser/feed/{dispenser_id}", dependencies=[Depends(get_current_user)])(get_level_feed)
app.get("/dispenser/levels/{dispenser_id}", dependencies=[Depends(get_current_user)])(get_levels)

# Rotas protegidas para pets
app.post("/pet/", dependencies=[Depends(get_current_user)])(create_pet)
app.get("/pet/{pet_id}", dependencies=[Depends(get_current_user)])(read_pet)
app.put("/pet/{pet_id}", dependencies=[Depends(get_current_user)])(update_pet)
app.delete("/pet/{pet_id}", dependencies=[Depends(get_current_user)])(delete_pet)
app.get("/pet/", dependencies=[Depends(get_current_user)])(list_pets)
