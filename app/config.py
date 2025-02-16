import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY" ,"")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    MONGO_URI: str = os.getenv("MONGO_URI")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()