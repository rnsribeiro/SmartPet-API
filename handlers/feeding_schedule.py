from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from handlers.auth import get_current_user

# Conexão com o MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
feeding_schedule_collection = db.feeding_schedule

# Modelo para criar um novo horário de alimentação
class FeedingScheduleCreate(BaseModel):
    dispenser_id: str
    feed_time: str  # Horário de alimentação no formato HH:MM
    amount: int  # Quantidade de ração

# Modelo para atualizar um horário de alimentação existente
class FeedingScheduleUpdate(BaseModel):
    feed_time: str | None = None
    amount: int | None = None

# Modelo para a resposta da API com a lista de horários de alimentação
class FeedingScheduleResponse(BaseModel):
    dispenser_id: str
    schedules: list[dict]  # Lista de horários de alimentação

# Handler para criar um novo horário de alimentação
def create_feeding_schedule(feeding_schedule: FeedingScheduleCreate, current_user: dict = Depends(get_current_user)):
    # Converte o feed_time para o formato datetime.time
    feed_time = datetime.strptime(feeding_schedule.feed_time, "%H:%M").time()

    # Define o período de 1 hora antes e depois do horário especificado
    one_hour_ago = (datetime.combine(datetime.today(), feed_time) - timedelta(hours=1)).strftime("%H:%M")
    one_hour_later = (datetime.combine(datetime.today(), feed_time) + timedelta(hours=1)).strftime("%H:%M")

    # Verifica se há algum horário de alimentação dentro do período de 1 hora
    conflicting_schedule = feeding_schedule_collection.find_one({
        "dispenser_id": ObjectId(feeding_schedule.dispenser_id),
        "feed_time": {"$gte": one_hour_ago, "$lte": one_hour_later}
    })

    if conflicting_schedule:
        raise HTTPException(status_code=400, detail="Cannot create feeding schedule within 1 hour of an existing schedule")

    # Converte feed_time para string antes de salvar
    new_schedule = feeding_schedule.dict()
    new_schedule["dispenser_id"] = ObjectId(feeding_schedule.dispenser_id)
    new_schedule["feed_time"] = feeding_schedule.feed_time  # Mantém como string HH:MM
    new_schedule["is_released"] = False  # Inicialmente, o alimento não foi liberado
    result = feeding_schedule_collection.insert_one(new_schedule)
    return {"message": "Feeding schedule added successfully"}

# Handler para listar os horários de alimentação de um dispenser específico
def list_feeding_schedules(dispenser_id: str, current_user: dict = Depends(get_current_user)):
    schedules = feeding_schedule_collection.find({"dispenser_id": ObjectId(dispenser_id)})
    schedule_list = [{
        "id": str(schedule["_id"]),
        "feed_time": schedule["feed_time"],  # Já está no formato HH:MM
        "amount": schedule["amount"],
        "is_released": schedule["is_released"]
    } for schedule in schedules]
    return FeedingScheduleResponse(
        dispenser_id=dispenser_id,
        schedules=schedule_list
    )

# Handler para atualizar um horário de alimentação
def update_feeding_schedule(schedule_id: str, schedule_data: FeedingScheduleUpdate, current_user: dict = Depends(get_current_user)):
    schedule = feeding_schedule_collection.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")

    update_data = {}
    if schedule_data.feed_time is not None:
        try:
            # Verifica se o feed_time está no formato HH:MM
            datetime.strptime(schedule_data.feed_time, "%H:%M")
            update_data["feed_time"] = schedule_data.feed_time
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid feed time format. Expected: HH:MM.")
    if schedule_data.amount is not None:
        update_data["amount"] = schedule_data.amount

    if update_data:
        feeding_schedule_collection.update_one({"_id": ObjectId(schedule_id)}, {"$set": update_data})
    
    return {"message": "Feeding schedule updated successfully"}

# Handler para pular uma refeição
def skip_feeding_schedule(schedule_id: str, current_user: dict = Depends(get_current_user)):
    result = feeding_schedule_collection.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": {"is_released": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")
    return {"message": "Feeding schedule skipped successfully"}

# Handler para deletar um horário de alimentação
def delete_feeding_schedule(schedule_id: str, current_user: dict = Depends(get_current_user)):
    result = feeding_schedule_collection.delete_one({"_id": ObjectId(schedule_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")
    return {"message": "Feeding schedule deleted successfully"}
