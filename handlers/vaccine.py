# vaccine.py
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from handlers.auth import get_current_user

# Conexão com o MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
pets_collection = db.pets
vaccines_collection = db.vaccines

# Modelo para a criação de uma nova vacina
class VaccineCreate(BaseModel):
    pet_id: str
    vaccine_name: str
    application_date: str  # Recebe como string para facilitar a conversão para datetime

# Modelo para atualizar uma vacina existente
class VaccineUpdate(BaseModel):
    vaccine_name: str | None = None
    application_date: str | None = None  # Recebe como string para conversão

# Handler para criar uma nova vacina para um pet
def create_vaccine(vaccine: VaccineCreate, current_user: dict = Depends(get_current_user)):
    # Verifica se o pet existe no banco de dados
    pet = pets_collection.find_one({"_id": ObjectId(vaccine.pet_id)})
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Converte a string para datetime
    try:
        application_date = datetime.strptime(vaccine.application_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application date format. Expected: YYYY-MM-DD.")

    # Cria um novo registro de vacina
    new_vaccine = {
        "pet_id": ObjectId(vaccine.pet_id),
        "vaccine_name": vaccine.vaccine_name,
        "application_date": application_date,
    }
    vaccines_collection.insert_one(new_vaccine)
    return {"message": "Vaccine added successfully"}

# Handler para listar as vacinas de um pet específico
# Handler para listar as vacinas de um pet específico, ordenadas por data de aplicação
def list_vaccines_by_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    # Verifica se o pet existe no banco de dados
    pet = pets_collection.find_one({"_id": ObjectId(pet_id)})
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Busca as vacinas do pet e ordena por `application_date` em ordem crescente
    vaccines = vaccines_collection.find({"pet_id": ObjectId(pet_id)}).sort("application_date", 1)  # 1 para ordem crescente e -1 para ordem decrescente
    
    vaccine_list = [{
        "id": str(v["_id"]),
        "vaccine_name": v["vaccine_name"],
        "application_date": v["application_date"].strftime("%Y-%m-%d")  # Converte datetime para string
    } for v in vaccines]

    return vaccine_list


# Handler para atualizar uma vacina
def update_vaccine(vaccine_id: str, vaccine_data: VaccineUpdate, current_user: dict = Depends(get_current_user)):
    # Verifica se a vacina existe no banco de dados
    vaccine = vaccines_collection.find_one({"_id": ObjectId(vaccine_id)})
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")

    update_data = {}
    if vaccine_data.vaccine_name is not None:
        update_data["vaccine_name"] = vaccine_data.vaccine_name
    if vaccine_data.application_date is not None:
        # Converte a string para datetime
        try:
            update_data["application_date"] = datetime.strptime(vaccine_data.application_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid application date format. Expected: YYYY-MM-DD.")

    if update_data:
        vaccines_collection.update_one({"_id": ObjectId(vaccine_id)}, {"$set": update_data})
    
    return {"message": "Vaccine updated successfully"}

# Handler para deletar uma vacina
def delete_vaccine(vaccine_id: str, current_user: dict = Depends(get_current_user)):
    # Verifica se a vacina existe no banco de dados
    vaccine = vaccines_collection.find_one({"_id": ObjectId(vaccine_id)})
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")

    vaccines_collection.delete_one({"_id": ObjectId(vaccine_id)})
    return {"message": "Vaccine deleted successfully"}
