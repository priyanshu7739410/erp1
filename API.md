# MediCloud Hospital ERP API Specification

Base URI: `/api/v1`

## 1. Authentication (`/auth`)
- `POST /auth/token`
  - **Payload**: `OAuth2PasswordRequestForm` (`username`, `password`)
  - **Returns**: JWT Bearer token (`access_token`, `token_type`)
- `POST /auth/register`
  - **Payload**: `UserCreate` (`username`, `email`, `password`, `role`)
  - **Returns**: Created `User` profile.

## 2. Patients (`/patients`)
- `POST /` - Register new patient.
- `GET /search` - Search by name, email, or phone.
- `GET /{id}` - Get patient profile and history summary.
- `PUT /{id}` - Update patient demographics.
- `DELETE /{id}` - Soft delete / deactivate patient record.

## 3. Doctors & Staff (`/doctors`, `/staff`, `/departments`)
- `GET /departments` - List hospital clinical departments.
- `GET /doctors` - List attending physicians.
- `POST /doctors` - Register new doctor.
- `GET /staff` - List hospital staff (nurses, receptionists, billing officers).

## 4. Appointments (`/appointments`)
- `POST /` - Schedule an appointment (enforces daily capacity of 16 appointments and checks doctor conflicts).
- `GET /` - List appointments filtered by doctor, patient, or date.
- `POST /{id}/checkin` - Mark appointment as checked-in.
- `POST /{id}/cancel` - Cancel appointment.

## 5. Medical Records (`/medical-records`)
- `POST /` - Submit clinical encounter note, diagnosis, and treatment plan (automatically completes linked appointment and generates invoice).
- `GET /` - List patient medical records.

## 6. Billing & Payments (`/billing`)
- `GET /invoices` - List active invoices.
- `GET /invoices/{id}` - Get detailed invoice and line items.
- `POST /payments` - Record payment capture and update invoice status.

## 7. Insurance Optimization (`/insurance`)
- `POST /policies/upload-text` - NLP rule-based extraction of policy clauses.
- `GET /policies` - List active patient policies.
- `POST /coverage-checks/{appt_id}` - Validate upcoming appointment against policy constraints.
- `GET /coverage-warnings` - List flagged or denied coverage risks.

## 8. Pharmacy & Inventory (`/inventory`)
- `GET /items` - List medications and supplies (filter by category or reorder alerts).
- `POST /items` - Add new inventory item.
- `POST /transactions` - Record stock movement (in/out/adjustment).
- `POST /prescriptions` - Write e-prescription.
- `POST /prescriptions/{id}/dispense` - Dispense medication and deduct from stock.
- `POST /purchase-orders` - Create supplier PO.
