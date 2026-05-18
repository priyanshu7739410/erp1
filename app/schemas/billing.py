from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LineItemCreate(BaseModel):
    description: str
    amount: float

class LineItemResponse(BaseModel):
    id: int
    description: str
    amount: float

    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    due_date: datetime
    line_items: List[LineItemCreate]

class PaymentCreate(BaseModel):
    invoice_id: int
    amount_paid: float
    method: str
    reference_number: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount_paid: float
    method: str
    paid_at: datetime
    reference_number: Optional[str] = None

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: Optional[int] = None
    invoice_date: datetime
    due_date: datetime
    total_amount: float
    status: str
    line_items: List[LineItemResponse]
    payments: List[PaymentResponse]

    class Config:
        from_attributes = True
