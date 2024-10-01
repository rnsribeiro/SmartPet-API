from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from handlers.auth import get_current_user

# Conexão com o MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
fooding_schedule_collection = db.fooding_schedule

# Modelo para criar um novo horário de alimentação
class FoodingScheduleCreate(BaseModel):
    dispenser_id: str
    food_time: str  # Horário de alimentação no formato HH:MM
    amount: int  # Quantidade de ração

# Modelo para atualizar um horário de alimentação existente
class FoodingScheduleUpdate(BaseModel):
    food_time: str | None = None
    amount: int | None = None

# Modelo para a resposta da API com a lista de horários de alimentação
class FoodingScheduleResponse(BaseModel):
    dispenser_id: str
    schedules: list[dict]  # Lista de horários de alimentação

# Handler para criar um novo horário de alimentação
def create_fooding_schedule(fooding_schedule: FoodingScheduleCreate, current_user: dict = Depends(get_current_user)):
    # Converte o food_time para o formato datetime.time
    food_time = datetime.strptime(fooding_schedule.food_time, "%H:%M").time()

    # Define o período de 1 hora antes e depois do horário especificado
    one_hour_ago = (datetime.combine(datetime.today(), food_time) - timedelta(hours=1)).strftime("%H:%M")
    one_hour_later = (datetime.combine(datetime.today(), food_time) + timedelta(hours=1)).strftime("%H:%M")

    # Verifica se há algum horário de alimentação dentro do período de 1 hora
    conflicting_schedule = fooding_schedule_collection.find_one({
        "dispenser_id": ObjectId(fooding_schedule.dispenser_id),
        "food_time": {"$gte": one_hour_ago, "$lte": one_hour_later}
    })

    if conflicting_schedule:
        raise HTTPException(status_code=400, detail="Cannot create fooding schedule within 1 hour of an existing schedule")

    # Converte food_time para string antes de salvar
    new_schedule = fooding_schedule.dict()
    new_schedule["dispenser_id"] = ObjectId(fooding_schedule.dispenser_id)
    new_schedule["food_time"] = fooding_schedule.food_time  # Mantém como string HH:MM
    new_schedule["is_released"] = False  # Inicialmente, o alimento não foi liberado
    result = fooding_schedule_collection.insert_one(new_schedule)
    return {"message": "Fooding schedule added successfully"}

# Handler para listar os horários de alimentação de um dispenser específico
def list_fooding_schedules(dispenser_id: str, current_user: dict = Depends(get_current_user)):
    schedules = fooding_schedule_collection.find({"dispenser_id": ObjectId(dispenser_id)})
    schedule_list = [{
        "id": str(schedule["_id"]),
        "food_time": schedule["food_time"],  # Já está no formato HH:MM
        "amount": schedule["amount"],
        "is_released": schedule["is_released"]
    } for schedule in schedules]
    return FoodingScheduleResponse(
        dispenser_id=dispenser_id,
        schedules=schedule_list
    )

# Handler para atualizar um horário de alimentação
def update_fooding_schedule(schedule_id: str, schedule_data: FoodingScheduleUpdate, current_user: dict = Depends(get_current_user)):
    schedule = fooding_schedule_collection.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(status_code=404, detail="Fooding schedule not found")

    update_data = {}
    if schedule_data.food_time is not None:
        try:
            # Verifica se o food_time está no formato HH:MM
            datetime.strptime(schedule_data.food_time, "%H:%M")
            update_data["food_time"] = schedule_data.food_time
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid food time format. Expected: HH:MM.")
    if schedule_data.amount is not None:
        update_data["amount"] = schedule_data.amount

    if update_data:
        fooding_schedule_collection.update_one({"_id": ObjectId(schedule_id)}, {"$set": update_data})
    
    return {"message": "Fooding schedule updated successfully"}

# Handler para pular uma refeição
def skip_fooding_schedule(schedule_id: str, current_user: dict = Depends(get_current_user)):
    result = fooding_schedule_collection.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": {"is_released": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fooding schedule not found")
    return {"message": "Fooding schedule skipped successfully"}

# Handler para deletar um horário de alimentação
def delete_fooding_schedule(schedule_id: str, current_user: dict = Depends(get_current_user)):
    result = fooding_schedule_collection.delete_one({"_id": ObjectId(schedule_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fooding schedule not found")
    return {"message": "Fooding schedule deleted successfully"}