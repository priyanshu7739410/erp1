import os
import sys
from datetime import datetime, timedelta
from app.database.session import SessionLocal, engine
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.staff import Staff
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.billing import Invoice, BillingLineItem, Payment
from app.models.inventory import InventoryItem, Prescription
from app.auth.hashing import get_password_hash

def seed_database():
    print("Connecting to database for seeding...")
    db = SessionLocal()
    try:
        # Check idempotency or run updates
        print("Running database seeding check and updates...")

        # Seed Departments
        dept_names = ["Cardiology", "Pediatrics", "General Medicine", "Emergency & ICU"]
        depts = {}
        for name in dept_names:
            dept = db.query(Department).filter(Department.name == name).first()
            if not dept:
                dept = Department(name=name, description=f"Specialized {name} department")
                db.add(dept)
                db.commit()
                db.refresh(dept)
            depts[name] = dept
        
        # Seed Users
        sample_users = [
            {"username": "admin", "email": "admin@hospital.erp", "pass": "admin123", "role": "admin"},
            {"username": "doctor_cardio", "email": "s.jenkins@hospital.erp", "pass": "doctor123", "role": "doctor"},
            {"username": "doctor_peds", "email": "m.vance@hospital.erp", "pass": "doctor123", "role": "doctor"},
            {"username": "receptionist1", "email": "claire.frontdesk@hospital.erp", "pass": "staff123", "role": "receptionist"},
            {"username": "nurse1", "email": "joy.nurse@hospital.erp", "pass": "staff123", "role": "nurse"},
            {"username": "pharmacist1", "email": "david.wong@hospital.erp", "pass": "staff123", "role": "pharmacist"},
            {"username": "billing_officer1", "email": "rachel.finance@hospital.erp", "pass": "staff123", "role": "billing_officer"},
            {"username": "patient_emily", "email": "emily.clark@mail.com", "pass": "patient123", "role": "patient"},
            {"username": "patient_robert", "email": "robert.taylor@mail.com", "pass": "patient123", "role": "patient"}
        ]
        
        for u in sample_users:
            user = db.query(User).filter(User.username == u["username"]).first()
            if not user:
                # If username not found, check if a user with this email already exists to update them
                user_by_email = db.query(User).filter(User.email == u["email"]).first()
                if user_by_email:
                    user_by_email.username = u["username"]
                    user_by_email.hashed_password = get_password_hash(u["pass"])
                    user_by_email.role = u["role"]
                else:
                    user = User(
                        username=u["username"],
                        email=u["email"],
                        hashed_password=get_password_hash(u["pass"]),
                        role=u["role"],
                        is_active=True
                    )
                    db.add(user)
        db.commit()

        # Seed Doctors
        doc_cardio = db.query(Doctor).filter(Doctor.email == "s.jenkins@hospital.erp").first()
        if not doc_cardio:
            doc_cardio = Doctor(
                first_name="Sarah", last_name="Jenkins", specialty="Cardiology",
                license_number="LIC-CARDIO-8891", phone="+1-555-0192",
                email="s.jenkins@hospital.erp", department_id=depts["Cardiology"].id, is_active=True
            )
            db.add(doc_cardio)

        doc_peds = db.query(Doctor).filter(Doctor.email == "m.vance@hospital.erp").first()
        if not doc_peds:
            doc_peds = Doctor(
                first_name="Marcus", last_name="Vance", specialty="Pediatrics",
                license_number="LIC-PEDS-3342", phone="+1-555-0144",
                email="m.vance@hospital.erp", department_id=depts["Pediatrics"].id, is_active=True
            )
            db.add(doc_peds)
        db.commit()

        # Seed Patients
        pat_emily = db.query(Patient).filter(Patient.email == "emily.clark@mail.com").first()
        if not pat_emily:
            pat_emily = Patient(
                name="Emily Clark", email="emily.clark@mail.com", age=28, gender="Female",
                phone="+1-555-9832", address="742 Evergreen Terrace, Springfield",
                emergency_contact="John Clark (Brother) - +1-555-2231",
                insurance_provider="Blue Shield Health",
                medical_history_summary="Mild asthma, allergic to penicillin", is_active=True
            )
            db.add(pat_emily)

        pat_robert = db.query(Patient).filter(Patient.email == "robert.taylor@mail.com").first()
        if not pat_robert:
            pat_robert = Patient(
                name="Robert Taylor", email="robert.taylor@mail.com", age=45, gender="Male",
                phone="+1-555-4420", address="101 Maple Ave, Shelbyville",
                emergency_contact="Martha Taylor (Wife) - +1-555-4491",
                insurance_provider="Aetna Care Plus",
                medical_history_summary="Hypertension under treatment", is_active=True
            )
            db.add(pat_robert)
        db.commit()

        # Seed Staff
        staff_claire = db.query(Staff).filter(Staff.email == "claire.frontdesk@hospital.erp").first()
        if not staff_claire:
            staff_claire = Staff(
                first_name="Claire", last_name="Redfield", role="receptionist",
                employee_id="EMP-REC-001", phone="+1-555-8811",
                email="claire.frontdesk@hospital.erp", department_id=depts["General Medicine"].id, is_active=True
            )
            db.add(staff_claire)

        staff_joy = db.query(Staff).filter(Staff.email == "joy.nurse@hospital.erp").first()
        if not staff_joy:
            staff_joy = Staff(
                first_name="Joy", last_name="Miller", role="nurse",
                employee_id="EMP-NUR-002", phone="+1-555-8822",
                email="joy.nurse@hospital.erp", department_id=depts["Emergency & ICU"].id, is_active=True
            )
            db.add(staff_joy)

        staff_david = db.query(Staff).filter(Staff.email == "david.wong@hospital.erp").first()
        if not staff_david:
            staff_david = Staff(
                first_name="David", last_name="Wong", role="pharmacist",
                employee_id="EMP-PHA-003", phone="+1-555-8833",
                email="david.wong@hospital.erp", department_id=depts["General Medicine"].id, is_active=True
            )
            db.add(staff_david)

        staff_rachel = db.query(Staff).filter(Staff.email == "rachel.finance@hospital.erp").first()
        if not staff_rachel:
            staff_rachel = Staff(
                first_name="Rachel", last_name="Green", role="billing_officer",
                employee_id="EMP-BIL-004", phone="+1-555-8844",
                email="rachel.finance@hospital.erp", department_id=depts["General Medicine"].id, is_active=True
            )
            db.add(staff_rachel)
        db.commit()

        # Refresh objects to ensure IDs
        doc_cardio = db.query(Doctor).filter(Doctor.email == "s.jenkins@hospital.erp").first()
        doc_peds = db.query(Doctor).filter(Doctor.email == "m.vance@hospital.erp").first()
        pat_emily = db.query(Patient).filter(Patient.email == "emily.clark@mail.com").first()
        pat_robert = db.query(Patient).filter(Patient.email == "robert.taylor@mail.com").first()

        # Seed Appointments
        if doc_cardio and pat_emily:
            appt1 = db.query(Appointment).filter(Appointment.patient_id == pat_emily.id, Appointment.doctor_id == doc_cardio.id).first()
            if not appt1:
                appt1 = Appointment(
                    patient_id=pat_emily.id, doctor_id=doc_cardio.id,
                    scheduled_start=datetime.now() + timedelta(days=1, hours=2),
                    scheduled_end=datetime.now() + timedelta(days=1, hours=3),
                    status="scheduled", reason="Routine Cardiac Evaluation", notes="Patient reports occasional shortness of breath"
                )
                db.add(appt1)

        if doc_peds and pat_robert:
            appt2 = db.query(Appointment).filter(Appointment.patient_id == pat_robert.id, Appointment.doctor_id == doc_peds.id).first()
            if not appt2:
                appt2 = Appointment(
                    patient_id=pat_robert.id, doctor_id=doc_peds.id,
                    scheduled_start=datetime.now() - timedelta(hours=3),
                    scheduled_end=datetime.now() - timedelta(hours=2),
                    status="completed", reason="Follow-up checkup", notes="Vitals normal, prescription renewed"
                )
                db.add(appt2)
        db.commit()

        # Seed Invoices
        if pat_emily:
            inv1 = db.query(Invoice).filter(Invoice.patient_id == pat_emily.id).first()
            if not inv1:
                inv1 = Invoice(
                    patient_id=pat_emily.id, due_date=datetime.now() + timedelta(days=14),
                    total_amount=250.00, status="pending"
                )
                db.add(inv1)
                db.commit()
                db.refresh(inv1)
                line1 = BillingLineItem(invoice_id=inv1.id, description="Cardiology Specialist Consultation", amount=200.00)
                line2 = BillingLineItem(invoice_id=inv1.id, description="ECG Diagnostic Test", amount=50.00)
                db.add_all([line1, line2])
                db.commit()

        if pat_robert:
            inv2 = db.query(Invoice).filter(Invoice.patient_id == pat_robert.id).first()
            if not inv2:
                inv2 = Invoice(
                    patient_id=pat_robert.id, due_date=datetime.now() + timedelta(days=7),
                    total_amount=150.00, status="paid"
                )
                db.add(inv2)
                db.commit()
                db.refresh(inv2)
                line3 = BillingLineItem(invoice_id=inv2.id, description="Pediatric Consultation", amount=150.00)
                pay = Payment(invoice_id=inv2.id, amount_paid=150.00, method="Credit Card", reference_number="TX-998811-P")
                db.add_all([line3, pay])
                db.commit()

        # Seed Inventory & Prescriptions
        inv_item1 = db.query(InventoryItem).filter(InventoryItem.sku == "MED-AMOX-500").first()
        if not inv_item1:
            inv_item1 = InventoryItem(
                name="Amoxicillin 500mg", sku="MED-AMOX-500", category="medication",
                unit="box", quantity=80, reorder_level=20, price=18.50, supplier="Global Pharma Inc"
            )
            db.add(inv_item1)

        inv_item2 = db.query(InventoryItem).filter(InventoryItem.sku == "SUP-N95-001").first()
        if not inv_item2:
            inv_item2 = InventoryItem(
                name="N95 Surgical Respirator", sku="SUP-N95-001", category="surgical",
                unit="piece", quantity=300, reorder_level=50, price=2.50, supplier="MedSupply Warehouse"
            )
            db.add(inv_item2)
        db.commit()

        if pat_emily and doc_cardio:
            pres = db.query(Prescription).filter(Prescription.patient_id == pat_emily.id).first()
            if not pres:
                pres = Prescription(
                    patient_id=pat_emily.id, doctor_id=doc_cardio.id, medication_name="Amoxicillin 500mg",
                    dosage="1 capsule (500mg)", frequency="3 times a day", duration_days=7,
                    status="active", notes="Take with food"
                )
                db.add(pres)
                db.commit()

        # Seed Insurance Policies & Coverage Reviews
        from app.models.insurance import InsurancePolicy, CoverageReview
        
        # 1. Emily Clark Insurance
        pol_emily = db.query(InsurancePolicy).filter(InsurancePolicy.patient_id == pat_emily.id).first()
        if not pol_emily:
            pol_emily = InsurancePolicy(
                patient_id=pat_emily.id,
                provider_name="Blue Shield Health",
                policy_number="POL-EMILY-123",
                group_number="GRP-9912",
                deductible=250.0,
                co_pay=20.0,
                coverage_summary="Premium comprehensive cardiac and general medical coverage.",
                network_status="in-network",
                exclusions="Cosmetic surgery, Experimental acupuncture",
                is_active=True
            )
            db.add(pol_emily)
            db.commit()
            db.refresh(pol_emily)

        # 2. Robert Taylor Insurance (Out of Network / Flagged)
        pol_robert = db.query(InsurancePolicy).filter(InsurancePolicy.patient_id == pat_robert.id).first()
        if not pol_robert:
            pol_robert = InsurancePolicy(
                patient_id=pat_robert.id,
                provider_name="Aetna Care Plus",
                policy_number="POL-ROBERT-456",
                group_number="GRP-8831",
                deductible=1000.0,
                co_pay=30.0,
                coverage_summary="Standard clinical care, out-of-network exclusions apply.",
                network_status="out-of-network",
                exclusions="Pediatrics, Child developmental therapy",
                is_active=True
            )
            db.add(pol_robert)
            db.commit()
            db.refresh(pol_robert)

        # Get appointments to link
        appt1 = db.query(Appointment).filter(Appointment.patient_id == pat_emily.id).first()
        appt2 = db.query(Appointment).filter(Appointment.patient_id == pat_robert.id).first()

        if appt1 and pol_emily:
            rev1 = db.query(CoverageReview).filter(CoverageReview.appointment_id == appt1.id).first()
            if not rev1:
                rev1 = CoverageReview(
                    patient_id=pat_emily.id,
                    appointment_id=appt1.id,
                    insurance_policy_id=pol_emily.id,
                    review_date=datetime.utcnow(),
                    status="approved",
                    coverage_issue="Coverage verified successfully",
                    recommended_actions="Proceed with appointment check-in",
                    estimated_patient_cost=20.0
                )
                db.add(rev1)

        if appt2 and pol_robert:
            rev2 = db.query(CoverageReview).filter(CoverageReview.appointment_id == appt2.id).first()
            if not rev2:
                rev2 = CoverageReview(
                    patient_id=pat_robert.id,
                    appointment_id=appt2.id,
                    insurance_policy_id=pol_robert.id,
                    review_date=datetime.utcnow(),
                    status="flagged",
                    coverage_issue="Insurance provider Aetna Care Plus is out-of-network for this hospital facility",
                    recommended_actions="Notify patient of out-of-network deductible requirements ($1000.00) before consultation",
                    estimated_patient_cost=150.0
                )
                db.add(rev2)
        db.commit()

        print("Database successfully seeded with robust role-based test data!")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
