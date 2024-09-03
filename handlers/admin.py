from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from handlers.auth import get_current_admin_user

# Conecte-se ao MongoDB
client = MongoClient("mongodb://smartpet:smartpet@localhost:27017/")
db = client.smartpet
users_collection = db.users
pets_collection = db.pets
dispensers_collection = db.dispensers

router = APIRouter()

@router.get("/users")
def admin_list_users(current_admin: dict = Depends(get_current_admin_user)):
    return list(users_collection.find({}, {"password": 0}))

@router.get("/pets")
def admin_list_pets(current_admin: dict = Depends(get_current_admin_user)):
    return list(pets_collection.find())

@router.get("/dispensers")
def admin_list_dispensers(current_admin: dict = Depends(get_current_admin_user)):
    return list(dispensers_collection.find())

@router.get("/user/{user_id}")
def admin_read_user(user_id: str, current_admin: dict = Depends(get_current_admin_user)):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/user/{user_id}/pets")
def admin_list_user_pets(user_id: str, current_admin: dict = Depends(get_current_admin_user)):
    return list(pets_collection.find({"owner": user_id}))

@router.get("/user/{user_id}/dispensers")
def admin_list_user_dispensers(user_id: str, current_admin: dict = Depends(get_current_admin_user)):
    return list(dispensers_collection.find({"owner": user_id}))