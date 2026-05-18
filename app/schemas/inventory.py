from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class InventoryItemCreate(BaseModel):
    name: str
    sku: str
    category: str
    unit: str
    quantity: int = 0
    reorder_level: int = 10
    price: float = 0.0
    supplier: Optional[str] = None

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    price: Optional[float] = None
    supplier: Optional[str] = None
    is_active: Optional[bool] = None

class InventoryItemResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    unit: str
    quantity: int
    reorder_level: int
    price: float
    supplier: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class StockTransactionCreate(BaseModel):
    item_id: int
    quantity_change: int
    transaction_type: str # in, out, adjustment
    notes: Optional[str] = None
    recorded_by: str

class StockTransactionResponse(BaseModel):
    id: int
    item_id: int
    quantity_change: int
    transaction_type: str
    date: datetime
    notes: Optional[str] = None
    recorded_by: str

    class Config:
        from_attributes = True

class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    notes: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderCreate(BaseModel):
    supplier_name: str
    item_id: int
    quantity: int

class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_name: str
    item_id: int
    quantity: int
    order_date: datetime
    status: str

    class Config:
        from_attributes = True
