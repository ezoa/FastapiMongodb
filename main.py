from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from database import database, collection

app = FastAPI()

# Pydantic Model for User
class User(BaseModel):
    name: str
    email: EmailStr

@app.post("/users/", response_model=User)
async def create_user(user: User):
    existing_user = await collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = await collection.insert_one(user.dict())
    return {**user.dict(), "id": str(new_user.inserted_id)}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return user
