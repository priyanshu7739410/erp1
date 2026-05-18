from sqlalchemy.orm import Session
from app.models.billing import Invoice, BillingLineItem, Payment
from app.models.appointment import Appointment
from app.schemas.billing import InvoiceCreate, PaymentCreate
from app.utils.exceptions import NotFoundException, BadRequestException
from app.utils.pagination import paginate
from datetime import datetime, timedelta

def create_invoice(db: Session, data: InvoiceCreate) -> Invoice:
    total = sum(item.amount for item in data.line_items)
    invoice = Invoice(
        patient_id=data.patient_id,
        appointment_id=data.appointment_id,
        due_date=data.due_date,
        total_amount=total,
        status="pending"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    for item in data.line_items:
        line = BillingLineItem(invoice_id=invoice.id, description=item.description, amount=item.amount)
        db.add(line)
        
    db.commit()
    db.refresh(invoice)
    return invoice

def auto_generate_invoice_for_appointment(db: Session, appointment_id: int) -> Invoice:
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise NotFoundException(detail="Appointment not found")
        
    existing = db.query(Invoice).filter(Invoice.appointment_id == appointment_id).first()
    if existing:
        return existing
        
    # Standard consultation charge
    due_date = datetime.utcnow() + timedelta(days=14)
    invoice_data = InvoiceCreate(
        patient_id=appt.patient_id,
        appointment_id=appt.id,
        due_date=due_date,
        line_items=[
            {"description": f"General Consultation - {appt.reason or 'Follow-up'}", "amount": 150.00}
        ]
    )
    return create_invoice(db, invoice_data)

def get_invoice(db: Session, invoice_id: int) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise NotFoundException(detail="Invoice not found")
    return invoice

def list_invoices(db: Session, patient_id: int = None, status: str = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(Invoice)
    if patient_id is not None:
        query = query.filter(Invoice.patient_id == patient_id)
    if status:
        query = query.filter(Invoice.status == status)
    return paginate(query.order_by(Invoice.invoice_date.desc()), page, size)

def record_payment(db: Session, data: PaymentCreate) -> Payment:
    invoice = get_invoice(db, data.invoice_id)
    if data.amount_paid <= 0:
        raise BadRequestException(detail="Payment amount must be greater than 0")
        
    payment = Payment(**data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Recalculate invoice status
    paid_total = sum(p.amount_paid for p in invoice.payments)
    if paid_total >= invoice.total_amount:
        invoice.status = "paid"
    elif paid_total > 0:
        invoice.status = "partially_paid"
    else:
        invoice.status = "pending"
        
    db.commit()
    db.refresh(invoice)
    return payment

def list_payments(db: Session, invoice_id: int = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(Payment)
    if invoice_id is not None:
        query = query.filter(Payment.invoice_id == invoice_id)
    return paginate(query.order_by(Payment.paid_at.desc()), page, size)
