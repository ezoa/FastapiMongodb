
from contextlib import asynccontextmanager

from fastapi import FastAPI,status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.encoders import jsonable_encoder
from collections import defaultdict
from config import BaseConfig
from routers.cars import router as cars_router
from routers.users import router as users_router 

import cloudinary


settings= BaseConfig()




cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)

@asynccontextmanager
# async def lifespan(app:FastAPI):
#     print("Starting")
#     yield
#     print("Shutting down")


# app= FastAPI(lifespan=lifespan)

async def lifespan(app:FastAPI):
    app.client=AsyncIOMotorClient(settings.DB_URL)
    app.db=app.client[settings.DB_NAME]
    try:
        app.client.admin.command("ping")
        print("Pinged your deployment you have successfully connected to mongodb")
        print(f"Mongo address: {settings.DB_URL}")

    except Exception as e:
        print(e)

    yield 
    print("shutting down Mongodb connection")
    app.client.close()

app= FastAPI(lifespan=lifespan)
app.include_router(cars_router, prefix="/cars", tags=["cars"])

@app.get("/")
async def get_root():
    return {"Message":"Root working!"}