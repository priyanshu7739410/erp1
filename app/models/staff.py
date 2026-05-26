from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from app.database.session import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # receptionist, nurse, billing_officer, pharmacist, etc.
    employee_id = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    salary = Column(Float, nullable=True)
    shift_time = Column(String, default="day", nullable=True)

