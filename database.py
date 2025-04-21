from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

from dotenv import load_dotenv
import os

#Load .env

load_dotenv()


# Get Mongodb


MONGO_URI= os.getenv("MONGO_URI")
DB_NAME= os.getenv("DB_NAME")


#INitialize  MongoDB connection


client= AsyncIOMotorClient(MONGO_URI)
database=client[DB_NAME]
collection=database["users"]

async def init_db():
    await collection.create_index([("email", ASCENDING)], unique=True)