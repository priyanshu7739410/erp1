from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, paid, partially_paid, cancelled

    line_items = relationship("BillingLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class BillingLineItem(Base):
    __tablename__ = "billing_line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="line_items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    amount_paid = Column(Float, nullable=False)
    method = Column(String, nullable=False)  # cash, card, insurance, transfer
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reference_number = Column(String, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
