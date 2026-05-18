from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.session import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    specialty = Column(String, nullable=False, index=True)
    license_number = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
