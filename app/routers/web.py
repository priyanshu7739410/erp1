from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database.session import get_db
from app.auth.jwt_handler import decode_access_token, create_access_token
from app.auth.hashing import verify_password
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.billing import Invoice, Payment
from app.models.insurance import CoverageReview, InsurancePolicy
from app.models.inventory import InventoryItem, Prescription
from app.models.department import Department
from app.models.staff import Staff
from app.schemas.user import UserCreate
from app.schemas.patient import PatientCreate
from app.schemas.appointment import AppointmentCreate
from app.schemas.medical_record import MedicalRecordCreate
from app.schemas.billing import PaymentCreate
from app.schemas.inventory import InventoryItemCreate, PrescriptionCreate
from app.services.auth_service import register_user
from app.services.patient_service import create_patient
from app.services.appointment_service import create_appointment, cancel_appointment
from app.services.medical_record_service import create_medical_record
from app.services.billing_service import record_payment, auto_generate_invoice_for_appointment
from app.services.insurance_service import extract_policy_from_text, validate_appointment_coverage
from app.services.inventory_service import create_item, create_prescription, dispense_prescription
from app.utils.limiter import limiter

router = APIRouter(tags=["Web UI"])
templates = Jinja2Templates(directory="app/templates")

def get_web_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if user:
        display_name = None
        if user.role in ["receptionist", "nurse", "pharmacist", "billing_officer"]:
            from app.models.staff import Staff
            staff = db.query(Staff).filter(Staff.email.ilike(user.email.strip())).first()
            if staff:
                display_name = f"{staff.first_name} {staff.last_name}"
        elif user.role == "doctor":
            from app.models.doctor import Doctor
            doctor = db.query(Doctor).filter(Doctor.email.ilike(user.email.strip())).first()
            if doctor:
                display_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        elif user.role == "patient":
            from app.models.patient import Patient
            patient = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
            if patient:
                display_name = patient.name
        
        user.display_name = display_name or user.username
    return user

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(request, "login.html", {"error": error})

@router.post("/login")
@limiter.limit("5/minute")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password"})
    
    token = create_access_token({"sub": user.username, "role": user.role})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {})

@router.post("/register")
@limiter.limit("5/minute")
def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("receptionist"),
    db: Session = Depends(get_db)
):
    try:
        user_data = UserCreate(username=username, email=email, password=password, role=role)
        register_user(db, user_data)
        if role == "patient":
            patient_data = PatientCreate(
                name=username,
                email=email,
                age=30,
                gender="Not Specified",
                phone="Pending Registration"
            )
            create_patient(db, patient_data)
        elif role in ["receptionist", "nurse", "pharmacist", "billing_officer"]:
            from app.models.staff import Staff
            existing_staff = db.query(Staff).filter(Staff.email.ilike(email.strip())).first()
            if not existing_staff:
                name_parts = username.split()
                first_name = name_parts[0].capitalize()
                last_name = name_parts[1].capitalize() if len(name_parts) > 1 else "Staff"
                import random
                emp_id = f"EMP-{role[:3].upper()}-{random.randint(100, 999)}"
                new_staff = Staff(
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    employee_id=emp_id,
                    phone="Pending",
                    email=email,
                    is_active=True
                )
                db.add(new_staff)
                db.commit()
        elif role == "doctor":
            from app.models.doctor import Doctor
            existing_doctor = db.query(Doctor).filter(Doctor.email.ilike(email.strip())).first()
            if not existing_doctor:
                name_parts = username.split()
                first_name = name_parts[0].capitalize()
                last_name = name_parts[1].capitalize() if len(name_parts) > 1 else "Doctor"
                new_doctor = Doctor(
                    first_name=first_name,
                    last_name=last_name,
                    specialty="General Medicine",
                    license_number="Pending",
                    phone="Pending",
                    email=email,
                    is_active=True
                )
                db.add(new_doctor)
                db.commit()
        return RedirectResponse(url="/login?message=Registration successful. Please log in.", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse(request, "register.html", {"error": str(e)})

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
        
    if user.role == "patient":
        p = db.query(Patient).filter((Patient.email.ilike(user.email.strip())) | (Patient.name == user.username)).first()
        pid = p.id if p else 0
        appointments = db.query(Appointment).filter(Appointment.patient_id == pid).order_by(Appointment.scheduled_start).all()
        invoices = db.query(Invoice).filter(Invoice.patient_id == pid).all()
        pending_invoices = [i for i in invoices if i.status != "paid"]
        pending_total = sum(i.total_amount for i in pending_invoices)
        stats = {
            "my_appointments_count": len(appointments),
            "pending_bills": f"${pending_total:.2f}",
            "paid_bills_count": len(invoices) - len(pending_invoices)
        }
        return templates.TemplateResponse(request, "dashboard_patient.html", {
            "user": user, "stats": stats, "appointments": appointments, "invoices": invoices
        })
    elif user.role == "doctor":
        d = db.query(Doctor).filter((Doctor.email.ilike(user.email.strip())) | (Doctor.first_name == user.username) | (Doctor.last_name == user.username)).first()
        did = d.id if d else 0
        appointments = db.query(Appointment).filter(Appointment.doctor_id == did).order_by(Appointment.scheduled_start).all()
        stats = {
            "my_patients_count": len(set(a.patient_id for a in appointments)),
            "my_appointments_count": len([a for a in appointments if a.status != "cancelled"]),
            "completed_consultations": len([a for a in appointments if a.status == "completed"])
        }
        return templates.TemplateResponse(request, "dashboard_doctor.html", {
            "user": user, "stats": stats, "appointments": appointments
        })
    elif user.role == "nurse":
        patients_count = db.query(Patient).filter(Patient.is_active == True).count()
        doctors_count = db.query(Doctor).filter(Doctor.is_active == True).count()
        appointments_count = db.query(Appointment).filter(Appointment.status != "cancelled").count()
        recent_appointments = db.query(Appointment).order_by(Appointment.scheduled_start).limit(5).all()
        stats = {
            "patients_count": patients_count,
            "doctors_count": doctors_count,
            "appointments_count": appointments_count
        }
        return templates.TemplateResponse(request, "dashboard_nurse.html", {
            "user": user, "stats": stats, "recent_appointments": recent_appointments
        })
    elif user.role == "pharmacist":
        total_items = db.query(InventoryItem).filter(InventoryItem.is_active == True).count()
        low_stock = db.query(InventoryItem).filter(InventoryItem.is_active == True, InventoryItem.quantity <= InventoryItem.reorder_level).count()
        pending_prescriptions = db.query(Prescription).filter(Prescription.status == "active").all()
        recent_items = db.query(InventoryItem).filter(InventoryItem.is_active == True).order_by(InventoryItem.name).limit(5).all()
        stats = {
            "total_items": total_items,
            "low_stock": low_stock,
            "pending_prescriptions_count": len(pending_prescriptions)
        }
        return templates.TemplateResponse(request, "dashboard_pharmacist.html", {
            "user": user, "stats": stats, "pending_prescriptions": pending_prescriptions[:5], "recent_items": recent_items
        })
    elif user.role == "billing_officer":
        patients_count = db.query(Patient).filter(Patient.is_active == True).count()
        unpaid_invoices = db.query(Invoice).filter(Invoice.status == "pending").all()
        paid_invoices = db.query(Invoice).filter(Invoice.status == "paid").all()
        total_collected = sum(inv.total_amount for inv in paid_invoices)
        total_pending = sum(inv.total_amount for inv in unpaid_invoices)
        recent_payments = db.query(Payment).order_by(Payment.paid_at.desc()).limit(5).all()
        stats = {
            "patients_count": patients_count,
            "unpaid_count": len(unpaid_invoices),
            "total_collected": f"{total_collected:.2f}",
            "total_pending": f"{total_pending:.2f}"
        }
        return templates.TemplateResponse(request, "dashboard_billing.html", {
            "user": user, "stats": stats, "unpaid_invoices": unpaid_invoices[:5], "recent_payments": recent_payments
        })

    patients_count = db.query(Patient).filter(Patient.is_active == True).count()
    doctors_count = db.query(Doctor).filter(Doctor.is_active == True).count()
    staff_count = db.query(Staff).filter(Staff.is_active == True).count()
    appointments_count = db.query(Appointment).filter(Appointment.status != "cancelled").count()
    
    pending_invoices = db.query(Invoice).filter(Invoice.status == "pending").all()
    pending_revenue = sum(inv.total_amount for inv in pending_invoices)
    
    recent_appointments = db.query(Appointment).order_by(Appointment.scheduled_start).limit(5).all()
    recent_warnings = db.query(CoverageReview).filter(CoverageReview.status != "approved").order_by(CoverageReview.review_date.desc()).limit(5).all()

    stats = {
        "patients_count": patients_count,
        "doctors_count": doctors_count,
        "staff_count": staff_count,
        "appointments_count": appointments_count,
        "pending_revenue": f"{pending_revenue:.2f}"
    }
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "stats": stats,
        "recent_appointments": recent_appointments,
        "recent_warnings": recent_warnings
    })

@router.get("/patients", response_class=HTMLResponse)
def patients_list(request: Request, q: Optional[str] = None, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "receptionist", "nurse", "billing_officer"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    
    query = db.query(Patient).filter(Patient.is_active == True)
    if q:
        query = query.filter(
            (Patient.name.ilike(f"%{q}%")) | (Patient.email.ilike(f"%{q}%")) | (Patient.phone.ilike(f"%{q}%"))
        )
    patients = query.order_by(Patient.name).all()
    return templates.TemplateResponse(request, "patients_list.html", {"user": user, "patients": patients, "query": q})

@router.get("/patients/new", response_class=HTMLResponse)
def new_patient_page(request: Request, user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "receptionist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    return templates.TemplateResponse(request, "patient_form.html", {"user": user})

@router.post("/patients/new")
def new_patient_post(
    request: Request,
    name: str = Form(...),
    email: Optional[str] = Form(None),
    age: int = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    emergency_contact: Optional[str] = Form(None),
    insurance_provider: Optional[str] = Form(None),
    medical_history_summary: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "receptionist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    data = PatientCreate(
        name=name, email=email if email else None, age=age, gender=gender, phone=phone,
        address=address, emergency_contact=emergency_contact, insurance_provider=insurance_provider,
        medical_history_summary=medical_history_summary
    )
    create_patient(db, data)
    return RedirectResponse(url="/patients", status_code=status.HTTP_302_FOUND)

@router.get("/patients/{patient_id}", response_class=HTMLResponse)
def patient_detail_page(request: Request, patient_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "nurse", "billing_officer", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        if not p or p.id != patient_id:
            raise HTTPException(status_code=403, detail="Access Denied")
            
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return RedirectResponse(url="/patients")
    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
    return templates.TemplateResponse(request, "patient_detail.html", {"user": user, "patient": patient, "records": records})

@router.get("/doctors", response_class=HTMLResponse)
def doctors_list_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "receptionist", "nurse", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
    return templates.TemplateResponse(request, "doctors_list.html", {"user": user, "doctors": doctors})

@router.get("/appointments", response_class=HTMLResponse)
def appointments_list_page(request: Request, date: Optional[str] = None, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "receptionist", "nurse", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
        
    query = db.query(Appointment)
    
    # Scope appointments by user role
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        query = query.filter(Appointment.patient_id == pid)
    elif user.role == "doctor":
        d = db.query(Doctor).filter((Doctor.email.ilike(user.email.strip())) | (Doctor.first_name == user.username) | (Doctor.last_name == user.username)).first()
        did = d.id if d else 0
        query = query.filter(Appointment.doctor_id == did)
        
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            day_start = target_date.replace(hour=0, minute=0, second=0)
            day_end = target_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Appointment.scheduled_start >= day_start, Appointment.scheduled_start <= day_end)
        except ValueError:
            pass
            
    appointments = query.order_by(Appointment.scheduled_start.desc()).all()
    
    # Calculate queue waiting numbers
    for appt in appointments:
        if appt.status == "checked_in":
            from datetime import time as dt_time
            start_date = appt.scheduled_start.date()
            day_start = datetime.combine(start_date, dt_time.min)
            day_end = datetime.combine(start_date, dt_time.max)
            earlier_checked_in = db.query(Appointment).filter(
                Appointment.doctor_id == appt.doctor_id,
                Appointment.status == "checked_in",
                Appointment.scheduled_start >= day_start,
                Appointment.scheduled_start <= day_end,
                Appointment.scheduled_start <= appt.scheduled_start
            ).count()
            appt.waiting_number = earlier_checked_in
        else:
            appt.waiting_number = None
            
    return templates.TemplateResponse(request, "appointments_list.html", {"user": user, "appointments": appointments, "date_filter": date})

@router.get("/appointments/new", response_class=HTMLResponse)
def new_appointment_page(request: Request, patient_id: Optional[int] = None, doctor_id: Optional[int] = None, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "receptionist", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
        
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        patient_id = p.id if p else None
        patients = [p] if p else []
    else:
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
    return templates.TemplateResponse(request, "appointment_form.html", {
        "user": user, "patients": patients, "doctors": doctors,
        "selected_patient_id": patient_id, "selected_doctor_id": doctor_id
    })

@router.post("/appointments/new")
def new_appointment_post(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    scheduled_start: str = Form(...),
    duration_minutes: int = Form(30),
    reason: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "receptionist", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        if not p or p.id != patient_id:
            raise HTTPException(status_code=403, detail="Access Denied")
    try:
        start_dt = datetime.fromisoformat(scheduled_start)
        from datetime import timedelta
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        data = AppointmentCreate(
            patient_id=patient_id, doctor_id=doctor_id, scheduled_start=start_dt, scheduled_end=end_dt, reason=reason, notes=notes
        )
        appt = create_appointment(db, data)
        validate_appointment_coverage(db, appt.id)
        return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
        return templates.TemplateResponse(request, "appointment_form.html", {
            "patients": patients, "doctors": doctors, "error": str(e)
        })

@router.get("/appointments/{appt_id:int}", response_class=HTMLResponse)
def appointment_detail_page(request: Request, appt_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "receptionist", "nurse", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        return RedirectResponse(url="/appointments?error=Appointment+not+found")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        if appt.patient_id != pid:
            raise HTTPException(status_code=403, detail="Access Denied")
    elif user.role == "doctor":
        d = db.query(Doctor).filter(Doctor.email.ilike(user.email.strip())).first()
        did = d.id if d else 0
        if appt.doctor_id != did:
            raise HTTPException(status_code=403, detail="Access Denied")
    
    # Get associated insurance coverage review
    coverage_review = db.query(CoverageReview).filter(CoverageReview.appointment_id == appt_id).first()
    
    return templates.TemplateResponse(request, "appointment_detail.html", {
        "user": user, 
        "appt": appt,
        "coverage_review": coverage_review
    })

@router.post("/appointments/{appt_id}/checkin")
def checkin_appointment(appt_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role not in ["admin", "receptionist", "nurse"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if appt and appt.status == "scheduled":
        appt.status = "checked_in"
        db.commit()
    return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)

@router.post("/appointments/{appt_id}/cancel")
def cancel_appointment_web(appt_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role not in ["admin", "receptionist", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        if appt.patient_id != pid:
            raise HTTPException(status_code=403, detail="Access Denied")
    cancel_appointment(db, appt_id)
    return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)

@router.get("/medical-records/new", response_class=HTMLResponse)
def new_medical_record_page(request: Request, appointment_id: Optional[int] = None, patient_id: Optional[int] = None, doctor_id: Optional[int] = None, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "nurse"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if appointment_id and (not patient_id or not doctor_id):
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appt:
            patient_id = appt.patient_id
            doctor_id = appt.doctor_id
    return templates.TemplateResponse(request, "medical_record_form.html", {
        "user": user, "appointment_id": appointment_id, "patient_id": patient_id, "doctor_id": doctor_id
    })

@router.post("/medical-records/new")
def new_medical_record_post(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    appointment_id: Optional[int] = Form(None),
    diagnosis: str = Form(...),
    notes: Optional[str] = Form(None),
    treatment_plan: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "doctor", "nurse"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    data = MedicalRecordCreate(
        patient_id=patient_id, doctor_id=doctor_id, appointment_id=appointment_id if appointment_id else None,
        diagnosis=diagnosis, notes=notes, treatment_plan=treatment_plan
    )
    create_medical_record(db, data)
    if appointment_id:
        auto_generate_invoice_for_appointment(db, appointment_id)
    return RedirectResponse(url=f"/patients/{patient_id}", status_code=status.HTTP_302_FOUND)

@router.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        invoices = db.query(Invoice).filter(Invoice.patient_id == pid).order_by(Invoice.invoice_date.desc()).all()
    elif user.role in ["admin", "billing_officer"]:
        invoices = db.query(Invoice).order_by(Invoice.invoice_date.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Access Denied")
    return templates.TemplateResponse(request, "billing_list.html", {"user": user, "invoices": invoices})

@router.get("/billing/invoices/{invoice_id}", response_class=HTMLResponse)
def invoice_detail_page(request: Request, invoice_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return RedirectResponse(url="/billing")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        if invoice.patient_id != pid:
            raise HTTPException(status_code=403, detail="Access Denied")
    elif user.role not in ["admin", "billing_officer"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    return templates.TemplateResponse(request, "invoice_detail.html", {"user": user, "invoice": invoice})

@router.post("/billing/payments")
def record_payment_web(
    request: Request,
    invoice_id: int = Form(...),
    amount_paid: float = Form(...),
    method: str = Form(...),
    reference_number: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "billing_officer", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        if invoice.patient_id != pid:
            raise HTTPException(status_code=403, detail="Access Denied")
    try:
        data = PaymentCreate(invoice_id=invoice_id, amount_paid=amount_paid, method=method, reference_number=reference_number)
        record_payment(db, data)
        return RedirectResponse(url=f"/billing/invoices/{invoice_id}", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        invoices = db.query(Invoice).order_by(Invoice.invoice_date.desc()).all()
        return templates.TemplateResponse(request, "billing_list.html", {"invoices": invoices, "error": str(e)})

@router.get("/insurance", response_class=HTMLResponse)
def insurance_redirect(user: Optional[User] = Depends(get_web_user)):
    if not user or user.role not in ["admin", "receptionist", "billing_officer", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    return RedirectResponse(url="/insurance/warnings")

@router.get("/insurance/warnings", response_class=HTMLResponse)
def insurance_warnings_page(request: Request, status: str = "flagged", db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "receptionist", "billing_officer", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
        
    policy = None
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.patient_id == pid).first()
        reviews = db.query(CoverageReview).filter(CoverageReview.patient_id == pid).order_by(CoverageReview.review_date.desc()).all()
    else:
        reviews = db.query(CoverageReview).filter(CoverageReview.status == status).order_by(CoverageReview.review_date.desc()).all()
        
    return templates.TemplateResponse(request, "insurance_warnings.html", {
        "user": user, "reviews": reviews, "policy": policy, "status_filter": status
    })

@router.get("/insurance/upload", response_class=HTMLResponse)
def insurance_upload_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "receptionist", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        patients = [p] if p else []
    else:
        patients = db.query(Patient).filter(Patient.is_active == True).all()
    return templates.TemplateResponse(request, "policy_upload.html", {"user": user, "patients": patients})

@router.post("/insurance/upload")
def insurance_upload_post(
    request: Request,
    patient_id: int = Form(...),
    policy_text: str = Form(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "receptionist", "patient"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if user.role == "patient":
        p = db.query(Patient).filter(Patient.email.ilike(user.email.strip())).first()
        pid = p.id if p else 0
        if patient_id != pid:
            raise HTTPException(status_code=403, detail="Access Denied")
    try:
        extract_policy_from_text(db, patient_id, policy_text)
        return RedirectResponse(url="/insurance/warnings", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        return templates.TemplateResponse(request, "policy_upload.html", {"patients": patients, "error": str(e)})

@router.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request, category: Optional[str] = None, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)
    if category:
        query = query.filter(InventoryItem.category == category)
    items = query.order_by(InventoryItem.name).all()
    prescriptions = db.query(Prescription).order_by(Prescription.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(request, "inventory_list.html", {
        "user": user, "items": items, "prescriptions": prescriptions, "category_filter": category
    })

@router.get("/inventory/new", response_class=HTMLResponse)
def new_inventory_page(request: Request, user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    return templates.TemplateResponse(request, "inventory_form.html", {"user": user})

@router.post("/inventory/new")
def new_inventory_post(
    request: Request,
    name: str = Form(...),
    sku: str = Form(...),
    category: str = Form(...),
    unit: str = Form(...),
    quantity: int = Form(50),
    reorder_level: int = Form(10),
    price: float = Form(15.00),
    supplier: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        data = InventoryItemCreate(
            name=name, sku=sku, category=category, unit=unit, quantity=quantity, reorder_level=reorder_level, price=price, supplier=supplier
        )
        create_item(db, data)
        return RedirectResponse(url="/inventory", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse(request, "inventory_form.html", {"error": str(e)})

@router.get("/prescriptions/new", response_class=HTMLResponse)
def new_prescription_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    patients = db.query(Patient).filter(Patient.is_active == True).all()
    if user.role == "doctor":
        d = db.query(Doctor).filter(Doctor.email.ilike(user.email.strip())).first()
        doctors = [d] if d else []
    else:
        doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
    return templates.TemplateResponse(request, "prescription_form.html", {"user": user, "patients": patients, "doctors": doctors})

@router.post("/prescriptions/new")
def new_prescription_post(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    medication_name: str = Form(...),
    dosage: str = Form(...),
    frequency: str = Form(...),
    duration_days: int = Form(7),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    if user.role == "doctor":
        d = db.query(Doctor).filter(Doctor.email.ilike(user.email.strip())).first()
        did = d.id if d else 0
        if doctor_id != did:
            raise HTTPException(status_code=403, detail="Access Denied")
    data = PrescriptionCreate(
        patient_id=patient_id, doctor_id=doctor_id, medication_name=medication_name,
        dosage=dosage, frequency=frequency, duration_days=duration_days, notes=notes
    )
    create_prescription(db, data)
    return RedirectResponse(url="/inventory", status_code=status.HTTP_302_FOUND)

@router.post("/prescriptions/{pres_id}/dispense")
def dispense_prescription_web(pres_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user:
        return RedirectResponse(url="/login")
    if user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        dispense_prescription(db, pres_id, dispensed_by=user.username)
    except Exception:
        pass
    return RedirectResponse(url="/inventory", status_code=status.HTTP_302_FOUND)

@router.get("/doctors/new", response_class=HTMLResponse)
def new_doctor_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")
    departments = db.query(Department).all()
    return templates.TemplateResponse(request, "doctor_form.html", {"user": user, "departments": departments})

@router.post("/doctors/new")
def new_doctor_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    specialty: str = Form(...),
    license_number: str = Form(...),
    phone: str = Form(...),
    department_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        # Check existing user
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise ValueError("Username or email already registered")
            
        existing_doctor = db.query(Doctor).filter((Doctor.license_number == license_number) | (Doctor.email == email)).first()
        if existing_doctor:
            raise ValueError("Doctor with this license or email already exists")

        # Create user
        from app.auth.hashing import get_password_hash
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role="doctor",
            is_active=True
        )
        db.add(new_user)
        
        # Create doctor
        dept_id = int(department_id) if (department_id and department_id.strip()) else None
        new_doctor = Doctor(
            first_name=first_name,
            last_name=last_name,
            specialty=specialty,
            license_number=license_number,
            phone=phone,
            email=email,
            department_id=dept_id,
            is_active=True
        )
        db.add(new_doctor)
        db.commit()
        return RedirectResponse(url="/doctors", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        departments = db.query(Department).all()
        return templates.TemplateResponse(request, "doctor_form.html", {
            "user": user, "departments": departments, "error": str(e)
        })

@router.get("/staff", response_class=HTMLResponse)
def staff_list_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")
    staff_members = db.query(Staff).order_by(Staff.is_active.desc(), Staff.first_name).all()
    return templates.TemplateResponse(request, "staff_list.html", {"user": user, "staff_members": staff_members})

@router.get("/staff/new", response_class=HTMLResponse)
def new_staff_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")
    departments = db.query(Department).all()
    return templates.TemplateResponse(request, "staff_form.html", {"user": user, "departments": departments, "action": "new"})

@router.post("/staff/new")
def new_staff_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(...),
    employee_id: str = Form(...),
    phone: str = Form(...),
    department_id: Optional[str] = Form(None),
    salary: Optional[float] = Form(None),
    shift_time: str = Form("day"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        # Validate existence
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise ValueError("Username or email already registered")
            
        existing_staff = db.query(Staff).filter((Staff.employee_id == employee_id) | (Staff.email == email)).first()
        if existing_staff:
            raise ValueError("Staff member with this employee ID or email already exists")

        # Create user
        from app.auth.hashing import get_password_hash
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        db.add(new_user)

        # Create staff
        dept_id = int(department_id) if (department_id and department_id.strip()) else None
        new_staff = Staff(
            first_name=first_name,
            last_name=last_name,
            role=role,
            employee_id=employee_id,
            phone=phone,
            email=email,
            department_id=dept_id,
            salary=salary,
            shift_time=shift_time,
            is_active=True
        )
        db.add(new_staff)
        db.commit()
        return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        departments = db.query(Department).all()
        return templates.TemplateResponse(request, "staff_form.html", {
            "user": user, "departments": departments, "error": str(e), "action": "new"
        })

@router.get("/staff/{staff_id}/edit", response_class=HTMLResponse)
def edit_staff_page(request: Request, staff_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")
    staff_member = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff_member:
        return RedirectResponse(url="/staff?error=Staff+member+not+found")
    departments = db.query(Department).all()
    
    # Try to find corresponding user for login details
    user_record = db.query(User).filter(User.email.ilike(staff_member.email.strip())).first()
    
    return templates.TemplateResponse(request, "staff_form.html", {
        "user": user, 
        "departments": departments, 
        "staff": staff_member, 
        "user_record": user_record,
        "action": "edit"
    })

@router.post("/staff/{staff_id}/edit")
def edit_staff_post(
    request: Request,
    staff_id: int,
    username: str = Form(...),
    email: str = Form(...),
    password: Optional[str] = Form(None),
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(...),
    employee_id: str = Form(...),
    phone: str = Form(...),
    department_id: Optional[str] = Form(None),
    salary: Optional[float] = Form(None),
    shift_time: str = Form("day"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_web_user)
):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access Denied")
    staff_member = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff_member:
        return RedirectResponse(url="/staff?error=Staff+member+not+found")
    
    try:
        # Check email/emp_id uniqueness (excluding self)
        existing_staff = db.query(Staff).filter(
            (Staff.id != staff_id) & ((Staff.employee_id == employee_id) | (Staff.email == email))
        ).first()
        if existing_staff:
            raise ValueError("Employee ID or Email already registered to another staff member")

        # Find corresponding user to update
        user_record = db.query(User).filter(User.email.ilike(staff_member.email.strip())).first()
        if user_record:
            user_record.username = username
            user_record.email = email
            user_record.role = role
            if password and password.strip():
                from app.auth.hashing import get_password_hash
                user_record.hashed_password = get_password_hash(password)
        else:
            # If no user exists yet, let's create one
            from app.auth.hashing import get_password_hash
            user_record = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password if password else "staff123"),
                role=role,
                is_active=True
            )
            db.add(user_record)

        # Update staff fields
        dept_id = int(department_id) if (department_id and department_id.strip()) else None
        staff_member.first_name = first_name
        staff_member.last_name = last_name
        staff_member.role = role
        staff_member.employee_id = employee_id
        staff_member.phone = phone
        staff_member.email = email
        staff_member.department_id = dept_id
        staff_member.salary = salary
        staff_member.shift_time = shift_time

        db.commit()
        return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        departments = db.query(Department).all()
        return templates.TemplateResponse(request, "staff_form.html", {
            "user": user, 
            "departments": departments, 
            "staff": staff_member,
            "error": str(e), 
            "action": "edit"
        })

@router.post("/staff/{staff_id}/toggle-active")
def toggle_staff_active(staff_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_web_user)):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access Denied")
    staff_member = db.query(Staff).filter(Staff.id == staff_id).first()
    if staff_member:
        staff_member.is_active = not staff_member.is_active
        # Also toggle active status of the corresponding User account
        user_record = db.query(User).filter(User.email.ilike(staff_member.email.strip())).first()
        if user_record:
            user_record.is_active = staff_member.is_active
        db.commit()
    return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)
