from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import ObjectId
from pydantic import BaseModel

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet  # Substitua 'mydatabase' pelo nome do seu banco de dados
dispensers_collection = db.dispensers  # Substitua 'dispensers' pelo nome da coleção que você deseja usar

# modelos para a criação de um novo dispenser
class DispenserCreate(BaseModel):    
    water: int
    feed: int
    
# modelos para a resposta da API com o ID e informações do dispenser
class Dispenser(BaseModel):
    id: str  # Usaremos o ID do MongoDB como uma string
    water: int
    feed: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de água
class WaterLevelUpdate(BaseModel):
    water: int

# Definindo o modelo Pydantic para o JSON de entrada para o nível de ração
class FeedLevelUpdate(BaseModel):
    feed: int

# Definindo o modelo Pydantic para o JSON de entrada para o nivel de ração e água
class LevelsUpdate(BaseModel):
    water: int
    feed: int

# Handler para criar um novo dispenser
def create_dispenser(dispenser: DispenserCreate):
    result = dispensers_collection.insert_one(dispenser.dict())
    return Dispenser(id=str(result.inserted_id), **dispenser.dict())

# Handler para atualizar o nível de água
def update_level_water(dispenser_id: str, level_water: WaterLevelUpdate):
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id)}, 
        {"$set": {"water": level_water.water}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Water level updated successfully"}

# Handler para atualizar o nivel de racao
def update_level_feed(dispenser_id: str, level_feed: FeedLevelUpdate):
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id)}, 
        {"$set": {"feed": level_feed.feed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Feed level updated successfully"}

# Handler para atualizar o nivel de agua e de racao
def update_levels(dispenser_id: str, levels_update: LevelsUpdate):
    level_water = levels_update.water
    level_feed = levels_update.feed    
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id)}, 
        {"$set": {"water": levels_update.water, "feed": levels_update.feed}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"message": "Levels updated successfully"}

# Handler para ler o nivel de agua
def get_level_water(dispenser_id: str):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"]}

# Handler para ler o nivel de racao
def get_level_feed(dispenser_id: str):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"feed": result["feed"]}

# Handler para ler o nivel de agua e de racao
def get_levels(dispenser_id: str):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return {"water": result["water"], "feed": result["feed"]}

# Handler para listar todos os dispensers
def list_dispensers():
    results = dispensers_collection.find()
    return [Dispenser(id=str(result["_id"]), **result) for result in results]