import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./erp.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecrethospitalerpjwtkey1234567890!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for ERP ease of use

settings = Settings()
