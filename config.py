from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    DB_URL: Optional[str]=None
    DB_NAME: Optional[str]=None 
    CLOUDINARY_SECRET_KEY:Optional[str]
    CLOUDINARY_API_KEY:Optional[str]
    CLOUDINARY_CLOUD_NAME:Optional[str]





    model_config= SettingsConfigDict(env_file=".env", extra="ignore")
   

