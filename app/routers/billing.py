from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.billing import InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentResponse
from app.services.billing_service import (
    create_invoice,
    auto_generate_invoice_for_appointment,
    get_invoice,
    list_invoices,
    record_payment,
    list_payments
)
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])
allow_staff = RoleChecker(["admin", "receptionist", "doctor", "nurse"])

@router.post("/invoices", response_model=InvoiceResponse, dependencies=[Depends(allow_staff)])
def create_new_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):
    return create_invoice(db, data)

@router.post("/invoices/auto-generate/{appointment_id}", response_model=InvoiceResponse, dependencies=[Depends(allow_staff)])
def auto_invoice_for_appt(appointment_id: int, db: Session = Depends(get_db)):
    return auto_generate_invoice_for_appointment(db, appointment_id)

@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse], dependencies=[Depends(allow_staff)])
def get_invoices(
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_invoices(db, patient_id=patient_id, status=status, page=page, size=size)

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse, dependencies=[Depends(allow_staff)])
def get_single_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return get_invoice(db, invoice_id)

@router.post("/payments", response_model=PaymentResponse, dependencies=[Depends(allow_staff)])
def make_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return record_payment(db, data)

@router.get("/payments", response_model=PaginatedResponse[PaymentResponse], dependencies=[Depends(allow_staff)])
def get_payments(
    invoice_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_payments(db, invoice_id=invoice_id, page=page, size=size)
