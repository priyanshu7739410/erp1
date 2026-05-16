from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.session import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    age = Column(Integer)

    gender = Column(String)

    phone = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)