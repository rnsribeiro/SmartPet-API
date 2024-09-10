from fastapi import HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from handlers.auth import get_current_user
from typing import Optional

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
pets_collection = db.pets

# Modelo para a criação e atualização de um pet
class PetCreate(BaseModel):
    name: str
    type_pet: str
    weight: float
    size: str
    age: int

# Modelo para a resposta da API com o ID e informações do pet
class Pet(BaseModel):
    id: str
    name: str
    type_pet: str
    weight: float
    size: str
    age: int
    owner: str

# Handler para criar um novo pet
def create_pet(pet: PetCreate, current_user: dict = Depends(get_current_user)):
    # Verificar se já existe um pet com o mesmo nome para este usuário
    existing_pet = pets_collection.find_one({
        "owner": str(current_user["_id"]),
        "name": pet.name
    })
    if existing_pet:
        raise HTTPException(status_code=400, detail="You already have a pet with this name")
    
    new_pet = pet.dict()
    new_pet["owner"] = str(current_user["_id"])
    result = pets_collection.insert_one(new_pet)
    return Pet(id=str(result.inserted_id), owner=new_pet["owner"], **pet.dict())

# Handler para ler os dados de um pet específico
def read_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    pet = pets_collection.find_one({"_id": ObjectId(pet_id), "owner": str(current_user["_id"])})
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found or you don't have permission to view it")
    return Pet(id=str(pet["_id"]), owner=pet["owner"], name=pet["name"], type_pet=pet["type_pet"], 
            weight=pet["weight"], size=pet["size"], age=pet["age"])

# Handler para atualizar os dados de um pet
def update_pet(pet_id: str, pet_update: PetCreate, current_user: dict = Depends(get_current_user)):
    # Verificar se o pet existe e pertence ao usuário
    existing_pet = pets_collection.find_one({"_id": ObjectId(pet_id), "owner": str(current_user["_id"])})
    if not existing_pet:
        raise HTTPException(status_code=404, detail="Pet not found or you don't have permission to update it")

    # Se o nome está sendo alterado, verificar se já existe outro pet com esse nome
    if existing_pet["name"] != pet_update.name:
        name_conflict = pets_collection.find_one({
            "owner": str(current_user["_id"]),
            "name": pet_update.name,
            "_id": {"$ne": ObjectId(pet_id)}  # Excluir o pet atual da busca
        })
        if name_conflict:
            raise HTTPException(status_code=400, detail="You already have another pet with this name")
    
    # Filtrar apenas os campos que podem ser atualizados
    update_data = {key: value for key, value in pet_update.dict().items() if key in ["name", "type_pet", "weight", "size", "age"]}
    
    # Atualizar o pet com os campos permitidos
    pets_collection.update_one(
        {"_id": ObjectId(pet_id)},
        {"$set": update_data}
    )

    # Buscar o pet atualizado para retorno
    updated_pet = pets_collection.find_one({"_id": ObjectId(pet_id)})
    return Pet(id=str(updated_pet["_id"]), **updated_pet)

# Handler para deletar um pet
def delete_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    result = pets_collection.delete_one({"_id": ObjectId(pet_id), "owner": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pet not found or you don't have permission to delete it")
    return {"message": "Pet deleted successfully"}

# Handler para listar todos os pets do usuário atual
def list_pets(current_user: dict = Depends(get_current_user)):
    pets = pets_collection.find({"owner": str(current_user["_id"])})
    return [Pet(id=str(pet["_id"]), owner=pet["owner"], name=pet["name"], type_pet=pet["type_pet"], 
            weight=pet["weight"], size=pet["size"], age=pet["age"]) for pet in pets]