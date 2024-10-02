from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
dispensers_collection = db.dispensers

# Modelos para a criação de um novo dispenser
class DispenserCreate(BaseModel):
    code: str  # O código será enviado pelo usuário
    water: int
    food: int
    
# Modelos para a resposta da API com o código do dispenser e suas informações
class Dispenser(BaseModel):
    code: str
    water: int
    food: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de água
class WaterLevelUpdate(BaseModel):
    code: str
    water: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de ração
class FoodLevelUpdate(BaseModel):
    code: str
    food: int

# Definindo o modelo Pydantic para o JSON de entrada para os níveis de água e ração
class LevelsUpdate(BaseModel):
    code: str
    water: int
    food: int

# Handler para criar um novo dispenser
def create_dispenser(dispenser: DispenserCreate):
    # Verificar se o código já está em uso
    if dispensers_collection.find_one({"code": dispenser.code}):
        raise HTTPException(status_code=400, detail="Code already in use")

    new_dispenser = dispenser.dict()
    result = dispensers_collection.insert_one(new_dispenser)
    return Dispenser(**new_dispenser)  # Corrigir esta linha

# Handler para atualizar o nível de água
def update_level_water(level_water: WaterLevelUpdate):
    result = dispensers_collection.update_one(
        {"code": level_water.code}, 
        {"$set": {"water": level_water.water}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Water level updated successfully"}

# Handler para atualizar o nível de ração
def update_level_food(level_food: FoodLevelUpdate):
    result = dispensers_collection.update_one(
        {"code": level_food.code}, 
        {"$set": {"food": level_food.food}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Food level updated successfully"}

# Handler para atualizar o nível de água e ração
def update_levels(levels_update: LevelsUpdate):
    result = dispensers_collection.update_one(
        {"code": levels_update.code}, 
        {"$set": {"water": levels_update.water, "food": levels_update.food}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Levels updated successfully"}

# Handler para ler o nível de água
def get_level_water(code: str):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"]}

# Handler para ler o nível de ração
def get_level_food(code: str):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"food": result["food"]}

# Handler para ler os níveis de água e ração
def get_levels(code: str):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"], "food": result["food"]}

# Handler para listar todos os dispensers
def list_dispensers():
    results = dispensers_collection.find({})
    return [Dispenser(code=result["code"], water=result["water"], food=result["food"]) for result in results]

# Handler para deletar um dispenser
def delete_dispenser(code: str):
    result = dispensers_collection.delete_one({"code": code})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Dispenser deleted successfully"}