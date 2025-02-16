import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY" ,"")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONOGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()