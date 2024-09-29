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
    code: int  # O código será enviado pelo usuário
    water: int
    feed: int
    
# Modelos para a resposta da API com o código do dispenser e suas informações
class Dispenser(BaseModel):
    code: int
    water: int
    feed: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de água
class WaterLevelUpdate(BaseModel):
    code: int
    water: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de ração
class FeedLevelUpdate(BaseModel):
    code: int
    feed: int

# Definindo o modelo Pydantic para o JSON de entrada para os níveis de água e ração
class LevelsUpdate(BaseModel):
    code: int
    water: int
    feed: int

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
def update_level_feed(level_feed: FeedLevelUpdate):
    result = dispensers_collection.update_one(
        {"code": level_feed.code}, 
        {"$set": {"feed": level_feed.feed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Feed level updated successfully"}

# Handler para atualizar o nível de água e ração
def update_levels(levels_update: LevelsUpdate):
    result = dispensers_collection.update_one(
        {"code": levels_update.code}, 
        {"$set": {"water": levels_update.water, "feed": levels_update.feed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Levels updated successfully"}

# Handler para ler o nível de água
def get_level_water(code: int):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"]}

# Handler para ler o nível de ração
def get_level_feed(code: int):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"feed": result["feed"]}

# Handler para ler os níveis de água e ração
def get_levels(code: int):
    result = dispensers_collection.find_one({"code": code})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"], "feed": result["feed"]}

# Handler para listar todos os dispensers
def list_dispensers():
    results = dispensers_collection.find({})
    return [Dispenser(code=result["code"], water=result["water"], feed=result["feed"]) for result in results]
