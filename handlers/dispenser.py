from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import ObjectId
from pydantic import BaseModel
from handlers.auth import get_current_user

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
dispensers_collection = db.dispensers

# modelos para a criação de um novo dispenser
class DispenserCreate(BaseModel):    
    water: int
    feed: int
    
# modelos para a resposta da API com o ID e informações do dispenser
class Dispenser(BaseModel):
    id: str
    water: int
    feed: int
    owner: str

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
def create_dispenser(dispenser: DispenserCreate, current_user: dict = Depends(get_current_user)):
    new_dispenser = dispenser.dict()
    new_dispenser["owner"] = str(current_user["_id"])
    result = dispensers_collection.insert_one(new_dispenser)
    return Dispenser(id=str(result.inserted_id), owner=new_dispenser["owner"], **dispenser.dict())

# Handler para atualizar o nível de água
def update_level_water(dispenser_id: str, level_water: WaterLevelUpdate, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])}, 
        {"$set": {"water": level_water.water}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to update it")
    return {"message": "Water level updated successfully"}

# Handler para atualizar o nivel de racao
def update_level_feed(dispenser_id: str, level_feed: FeedLevelUpdate, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])}, 
        {"$set": {"feed": level_feed.feed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to update it")
    return {"message": "Feed level updated successfully"}

# Handler para atualizar o nivel de agua e de racao
def update_levels(dispenser_id: str, levels_update: LevelsUpdate, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.update_one(
        {"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])}, 
        {"$set": {"water": levels_update.water, "feed": levels_update.feed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to update it")
    return {"message": "Levels updated successfully"}

# Handler para ler o nivel de agua
def get_level_water(dispenser_id: str, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to view it")
    return {"water": result["water"]}

# Handler para ler o nivel de racao
def get_level_feed(dispenser_id: str, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to view it")
    return {"feed": result["feed"]}

# Handler para ler o nivel de agua e de racao
def get_levels(dispenser_id: str, current_user: dict = Depends(get_current_user)):
    result = dispensers_collection.find_one({"_id": ObjectId(dispenser_id), "owner": str(current_user["_id"])})
    if result is None:
        raise HTTPException(status_code=404, detail="Dispenser not found or you don't have permission to view it")
    return {"water": result["water"], "feed": result["feed"]}

# Handler para listar todos os dispensers do usuário atual
def list_dispensers(current_user: dict = Depends(get_current_user)):
    results = dispensers_collection.find({"owner": str(current_user["_id"])})
    return [Dispenser(id=str(result["_id"]), owner=result["owner"], water=result["water"], feed=result["feed"]) for result in results]