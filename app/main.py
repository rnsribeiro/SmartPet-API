from fastapi import FastAPI, Depends
from handlers.user import create_user, read_user, list_users, update_user, delete_user
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
from handlers.vaccine import create_vaccine, list_vaccines_by_pet, update_vaccine, delete_vaccine
from handlers.feeding_schedule import (
    create_feeding_schedule,
    list_feeding_schedules,
    update_feeding_schedule,
    skip_feeding_schedule,
    delete_feeding_schedule,  # Import do novo handler para deletar
)

app = FastAPI()

# Rota de login
app.post("/token")(login_for_access_token)

# Rotas protegidas para usuários
app.post("/user/")(create_user)
app.get("/user/{user_id}", dependencies=[Depends(get_current_user)])(read_user)
app.get("/user/", dependencies=[Depends(get_current_user)])(list_users)
app.put("/user/{user_id}", dependencies=[Depends(get_current_user)])(update_user)
app.delete("/user/{user_id}", dependencies=[Depends(get_current_user)])(delete_user)

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

# Rotas protegidas para vacinas
app.post("/vaccine/")(create_vaccine)
app.get("/vaccine/{pet_id}")(list_vaccines_by_pet)
app.put("/vaccine/{vaccine_id}")(update_vaccine)
app.delete("/vaccine/{vaccine_id}")(delete_vaccine)

# Rotas protegidas para horários de alimentação
app.post("/feeding_schedule/", dependencies=[Depends(get_current_user)])(create_feeding_schedule)
app.get("/feeding_schedule/{dispenser_id}", dependencies=[Depends(get_current_user)])(list_feeding_schedules)
app.put("/feeding_schedule/{schedule_id}", dependencies=[Depends(get_current_user)])(update_feeding_schedule)
app.patch("/feeding_schedule/skip/{schedule_id}", dependencies=[Depends(get_current_user)])(skip_feeding_schedule)  # Rota para pular refeição
app.delete("/feeding_schedule/{schedule_id}", dependencies=[Depends(get_current_user)])(delete_feeding_schedule)  # Rota para deletar horário
