from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False) # medication, surgical, consumable
    unit = Column(String, nullable=False) # box, vial, tablet, piece
    quantity = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    price = Column(Float, default=0.0)
    supplier = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    quantity_change = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False) # in, out, adjustment
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String, nullable=True)
    recorded_by = Column(String, nullable=False)

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    medication_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    status = Column(String, default="active") # active, dispensed, cancelled
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="ordered") # ordered, received, cancelled
