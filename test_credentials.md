# 🔑 MediCloud Hospital ERP — Role-Based Test Credentials

Use these pre-seeded accounts to explore the custom role-based dashboards, navigation menus, and specialized features across the clinical, financial, and administrative modules.

---

## 🛡️ Executive & Administration

| Role | Username | Password | Email | Main Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | `admin@hospital.erp` | Full access across all modules, clinical oversight, revenue tracking, user management. |

---

## 👨‍⚕️ Clinical Faculty

| Role | Doctor Name | Specialty | Username | Password | Email |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Doctor** | Dr. Sarah Jenkins | Cardiology | `doctor_cardio` | `doctor123` | `s.jenkins@hospital.erp` |
| **Doctor** | Dr. Marcus Vance | Pediatrics | `doctor_peds` | `doctor123` | `m.vance@hospital.erp` |

**Doctor Dashboard Features:**
- **My Shift & Consultation Schedule:** View assigned patient appointments.
- **Encounter Documentation:** Log diagnoses and visit notes.
- **E-Prescribing:** Issue digital prescriptions directly to the hospital pharmacy.

---

## 🤒 Registered Patients

| Role | Patient Name | Insurance Provider | Username | Password | Email |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Patient** | Emily Clark | Blue Shield Health | `patient_emily` | `patient123` | `emily.clark@mail.com` |
| **Patient** | Robert Taylor | Aetna Care Plus | `patient_robert` | `patient123` | `robert.taylor@mail.com` |

**Patient Portal Features:**
- **My Appointments:** Track scheduled visits and past consultations.
- **Outstanding Invoices:** View itemized clinical charges and pay bills online.
- **Insurance Coverage:** Check policy pre-authorization warnings.

---

## 🏥 Hospital Staff & Operations

| Role | Staff Member | Department | Username | Password | Email |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Receptionist** | Claire Redfield | Front Desk / Admission | `receptionist1` | `staff123` | `claire.frontdesk@hospital.erp` |
| **Nurse** | Joy Miller | Emergency & ICU | `nurse1` | `staff123` | `joy.nurse@hospital.erp` |
| **Pharmacist** | David Wong | Pharmacy & Inventory | `pharmacist1` | `staff123` | `david.wong@hospital.erp` |
| **Billing Officer** | Rachel Green | Finance & Accounting | `billing_officer1` | `staff123` | `rachel.finance@hospital.erp` |

**Staff Capabilities:**
- **Receptionist:** Register walk-in patients and manage the master appointment calendar.
- **Nurse:** Triage patients and manage inpatient bed availability.
- **Pharmacist:** Dispense medications, deduct stock, and generate supplier purchase orders.
- **Billing Officer:** Generate medical invoices and record payment receipts.

---

## 🧪 Testing Instructions

1. Start your local development environment:
   ```bash
   docker compose up -d
   ```
2. Open your web browser and navigate to:
   ```url
   http://localhost:8000/login
   ```
3. Test switching between accounts (e.g., log in as `patient_emily`, view her pending $250.00 cardiology bill, then log out and log in as `doctor_cardio` to view her appointment!).
