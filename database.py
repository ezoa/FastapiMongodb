import os
from motor.motor_asyncio import AsyncIOMotorClient

# Define MongoDB connection URL
DB_URL = "mongodb://user:pass@mongodb:27017"
DB_NAME = "carBackend"

# Connect to MongoDB
client = AsyncIOMotorClient(DB_URL)
database = client[DB_NAME]

async def get_database():
    return database
