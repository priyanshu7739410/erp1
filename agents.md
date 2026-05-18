# Full Hospital ERP Project Plan

## Overview

This document describes a full Hospital ERP implementation plan built on the current repository structure. It is intentionally detailed and incremental, so you can expand the existing backend step by step without losing architectural clarity.

The current codebase already contains a working FastAPI application, SQLAlchemy models, Pydantic schemas, services, routers, PostgreSQL Docker support, and Alembic migrations. The ERP plan builds from this foundation.

## Current Architecture Snapshot

Existing folders and their purpose:

- `app/main.py`
  - Bootstraps FastAPI and registers routers.
- `app/database/database.py`
  - Creates the SQLAlchemy engine and session dependency.
- `app/models/`
  - Holds ORM models for database tables. Currently only `Patient`.
- `app/schemas/`
  - Contains Pydantic request/response models. Currently only `Patient` schemas.
- `app/services/`
  - Business logic layer. Currently `PatientService` handles patient CRUD.
- `app/routers/`
  - API route definitions. Currently patient CRUD routes.
- `Dockerfile` and `docker-compose.yml`
  - Containerize the API and PostgreSQL database.
- `requirements.txt`
  - Python dependencies.
- `alembic/`
  - Migration tooling for evolving the database schema.

## Full ERP Scope

A complete Hospital ERP should support at least the following functional areas:

1. Patients
2. Doctors and staff
3. Appointments and scheduling
4. Medical records and encounters
5. Billing and payments
6. Insurance optimization and claims validation
7. Inventory and pharmacy
8. Authentication and authorization
9. Reporting and analytics
10. Notifications and audit logs
11. Python-based frontend user interface

## Guiding Principles

- Keep routes thin. All logic should live in services.
- Keep schemas separate from models. Models are DB objects, schemas are API contracts.
- Use dependency injection for DB sessions, auth, and configuration.
- Use PostgreSQL as the primary data store.
- Use Docker compose to keep development reproducible.
- Use Alembic for schema migrations.
- Prefer Python-based frontend frameworks only; avoid JavaScript-only UI frameworks so the project stays in the Python stack.
- Add automated tests before expanding each major module.
- Maintain a clear boundary between domain modules.

---

# Autonomous Agent Execution and Anti-Drift Rules

## One-Go Autonomous Development

The system should be designed so AI coding agents can execute large portions of the ERP build in one continuous run without constantly stopping for clarification.

Agents should:

* understand the full repository structure before making changes
* plan dependencies before editing files
* create complete vertical slices of functionality:

  * model
  * schema
  * service
  * router
  * migration
  * tests
* continue execution automatically after fixing errors
* avoid partial implementations unless explicitly requested
* maintain architectural consistency across all modules
* update imports and dependency wiring automatically
* verify Docker/container health before continuing
* run migrations and tests after major changes
* self-correct failing builds before stopping

---

# Anti-Gravity Architecture Principle

The project must resist “architecture collapse” as complexity grows.

This means the system should naturally remain maintainable even as more modules, agents, and contributors are added.

## Anti-Gravity Rules

### 1. Prevent Architectural Drift

Agents must NOT:

* place business logic in routers
* directly access the database from UI code
* duplicate schemas or services
* create circular imports
* bypass service layers
* create giant utility files
* mix authentication logic into domain modules

All logic should remain modular and domain-driven.

---

### 2. Container Isolation First

Every major service or experimental feature should run in isolated Docker containers so failures do not corrupt the host machine or other services.

Requirements:

* every service starts inside Docker
* no direct host dependency pollution
* reproducible environments only
* separate containers for:

  * API
  * PostgreSQL
  * Redis
  * Celery workers
  * background jobs
  * monitoring stack
  * load testing
* use Docker volumes carefully
* agents must never install random global packages on the host machine

---

### 3. Self-Healing Development Flow

Agents should automatically:

* detect broken imports
* detect failing migrations
* repair dependency conflicts
* restart failed containers
* retry failed builds
* regenerate lock files if corrupted
* resolve schema mismatches
* keep the project runnable at all times

The repository should never remain in a half-broken state after execution.

---

### 4. Scalability by Default

All new modules should be implemented assuming future scale.

Requirements:

* PostgreSQL as primary relational database
* Redis for caching and queues
* async-ready FastAPI architecture
* service layer abstraction
* pagination everywhere
* indexing strategy from the beginning
* background jobs for heavy operations
* API versioning
* environment-based configuration
* centralized logging
* audit trails

---

### 5. Long-Horizon Engineering

Agents should optimize for:

* maintainability over shortcuts
* readability over cleverness
* extensibility over hardcoding
* production patterns over tutorial code

The goal is to build a production-style ERP system that can evolve for years without requiring a rewrite.

---

# Continuous Validation Pipeline

After every major implementation step, agents should automatically:

1. run formatting
2. run linting
3. run type checks
4. run migrations
5. run tests
6. rebuild containers
7. validate API startup
8. confirm Swagger/OpenAPI works

Suggested tools:

* `pytest`
* `ruff`
* `black`
* `mypy`
* `alembic`
* `docker compose`
* `k6` for load testing

---

# Agent Execution Priority

Agents should follow this order strictly:

1. architecture consistency
2. database correctness
3. API stability
4. authentication/security
5. business logic
6. test coverage
7. UI polish
8. optimization

Never sacrifice architecture for speed.

---

# Large-Scale Execution Rule

When implementing a feature, agents should complete the ENTIRE feature lifecycle in one run whenever possible:

* model
* schema
* service
* router
* migration
* permissions
* validation
* tests
* Docker verification
* API documentation

Avoid stopping after generating only partial code.

---

# Phase 0 — Stabilize Existing Foundation

## 0.1 Confirm the current patient module works

- Validate `app/main.py` includes patient router.
- Verify patient CRUD through API.
- Ensure DB connection works with Docker Compose.
- Add a minimal `/health` endpoint if desired.

## 0.2 Add basic error handling

- Create `app/utils/exceptions.py` with custom exception helpers.
- Add middleware or exception handlers in `app/main.py` for `HTTPException` and validation errors.
- Standardize error responses.

## 0.3 Add project documentation files

- Add `README.md` describing how to run the app with Docker.
- Add `commands.md` with build, run, test, and migration commands.

---

# Phase 1 — Core Clinical Domain

The first major extension is to model the clinical workflow: patients, doctors, appointments, and records.

## 1.1 Patients (complete)

### Deliverables

- Existing `Patient` model is finalized.
- Add fields and relationships as needed:
  - `address`
  - `emergency_contact`
  - `insurance_provider`
  - `medical_history_summary`
- Add index on `email` and possibly `phone`.

### Files impacted

- `app/models/patient.py`
- `app/schemas/patient.py`
- `app/services/patient.py`
- `app/routers/patient.py`
- Alembic migration to update schema if adding fields.

## 1.2 Users and Authentication

### Deliverables

- Add `app/models/user.py` and `app/schemas/user.py`.
- Add `app/services/auth.py` for password hashing and JWT.
- Add `app/routers/auth.py` for login/register.
- Add `app/auth/__init__.py` to centralize security utilities.
- Add roles: `admin`, `doctor`, `receptionist`, `nurse`.
- Protect API routes by role.

### Why this first?

Auth is required before most ERP workflows can be secure. It also enables role-based access for doctors, staff, and admins.

### Files impacted

- `app/auth/`
- `app/models/user.py`
- `app/schemas/user.py`
- `app/services/auth.py`
- `app/routers/auth.py`
- `app/main.py`

## 1.3 Doctors and Staff

### Deliverables

- Add `Doctor` and `Staff` models.
- `Doctor` fields: `first_name`, `last_name`, `specialty`, `license_number`, `phone`, `email`, `department`, `is_active`.
- `Staff` fields: `role`, `department`, `employee_id`, `phone`, `email`.
- Add CRUD routers and services.
- Add `DoctorResponse` and `DoctorCreate` schemas.

### Relationships

- `Appointment` will relate to `Doctor`.
- `Appointment` may relate to `Staff` for scheduling support.

## 1.4 Appointments and Scheduling

### Deliverables

- Add `Appointment` model.
- Fields:
  - `patient_id`
  - `doctor_id`
  - `scheduled_start`
  - `scheduled_end`
  - `status` (`scheduled`, `checked_in`, `completed`, `cancelled`)
  - `reason`
  - `notes`
- Add service methods for:
  - creating appointments
  - listing by patient/doctor/day
  - cancelling and rescheduling
- Add router endpoints for appointment management.

### Business logic

- Prevent overlapping appointments for the same doctor.
- Enforce a maximum daily appointment window.
- Use transactions for create/update operations.

## 1.5 Medical Records / Encounters

### Deliverables

- Add `MedicalRecord` or `Encounter` model.
- Fields: `patient_id`, `doctor_id`, `appointment_id`, `notes`, `diagnosis`, `treatment_plan`, `documents`, `created_at`.
- Create schemas and service layer for encounter notes.
- Add API routes for writing and retrieving patient visit records.

### Why this matters

Clinical data is the heart of any ERP. Storing encounters separately keeps appointment scheduling and medical history decoupled.

---

# Phase 2 — Financial and Operations Domain

Once the clinical data model is stable, extend ERP to support billing, payments, inventory, and pharmacy.

## 2.1 Billing and Payments

### Deliverables

- Add `Invoice` model.
- Add `Payment` model.
- Add `BillingLineItem` model for detailed charges.
- Fields for invoices:
  - `patient_id`, `appointment_id`, `invoice_date`, `due_date`, `total_amount`, `status`.
- Fields for payments:
  - `invoice_id`, `amount_paid`, `method`, `paid_at`, `reference_number`.

### Service logic

- Generate invoices automatically when appointments are completed.
- Apply payments to invoices and update invoice status.
- Support partial payments and refunds.

### Routes

- `POST /api/v1/billing/invoices`
- `GET /api/v1/billing/invoices`
- `POST /api/v1/billing/payments`
- `GET /api/v1/billing/payments`

## 2.2 Insurance Optimization and Claims Validation

### Why this is the top feature

Insurance is currently handled manually in the hospital insurance section. This module should help both patients and hospital staff avoid claim failures, reduce unexpected out-of-pocket costs, and maximize insurance coverage. It should work before a normal appointment so the system can flag policy mismatches or coverage gaps early.

### Deliverables

- Add `InsurancePolicy` model to store parsed policy coverage rules, service limits, co-pay percentages, exclusions, and network restrictions.
- Add `InsuranceClaimCheck` or `CoverageReview` model to track pre-authorization checks and potential payment risks.
- Add insurance policy ingestion and normalization logic. This can use a free text-based reading approach rather than a proprietary paid RAG service, with a local extraction pipeline for policy clauses.
- Add APIs for:
  - uploading or linking patient insurance policies
  - validating upcoming appointments against policy rules
  - generating warnings when appointments are likely to be denied or partially covered.

### Business logic

- Evaluate patient insurance policies against doctor specialty, procedure codes, appointment type, and hospital network status.
- Identify coverage gaps, pre-authorization needs, provider network mismatches, and exclusions before the appointment.
- Notify patients and administrative staff when an appointment is at risk of claim denial.
- Record a `coverage_issue` reason with severity and recommended actions.

### Design notes

- A lightweight local policy reading tool can extract key insurance terms from uploaded policy text. This is similar to RAG, but can be implemented with open-source or rule-based parsing to keep it free to read policies.
- Store policy clauses in structured fields so the system can compute allowed services, excluded treatments, and provider restrictions.
- Use `InsurancePolicy` data to enrich appointment booking and billing workflows.

### Example routes

- `POST /api/v1/insurance/policies`
- `GET /api/v1/insurance/policies/{patient_id}`
- `POST /api/v1/insurance/coverage-checks`
- `GET /api/v1/insurance/coverage-warnings?patient_id=`

## 2.3 Inventory and Pharmacy

### Deliverables

- Add `Medication` / `InventoryItem` models.
- Add `PurchaseOrder` and `StockTransaction` models.
- Track stock levels, reorder points, and dispensing history.
- Add `Prescription` model linking doctor, patient, medication, dosage, frequency, and status.

### Why this matters

Hospital ERPs must track medication inventory and ensure pharmacy dispensing is controlled.

## 2.3 Laboratory and Diagnostics (Optional)

### Deliverables

- Add `LabTest` model.
- Add `LabOrder` and `LabResult` models.
- Allow doctors to order tests and receive results.

### Use case

This is useful once the ERP is stable and you want to support hospital diagnostic workflows.

---

# Phase 3 — Supporting Services and Production Readiness

## 3.1 Logging, Monitoring, and Audit Trails

### Deliverables

- Add request logging middleware.
- Add audit table(s) for create/update/delete events.
- Track `created_by` and `updated_by` on important records.
- Add `app/utils/logging.py` or integrate Python `logging` config.

## 3.2 Pagination, Filtering, and Search

### Deliverables

- Add query pagination helpers in `app/utils/pagination.py`.
- Add filtering by date range, status, doctor, patient.
- Add search endpoints for patients and appointments.

## 3.3 Tests

### Deliverables

- Add unit tests for services and routers.
- Add integration tests for the API with a test database.
- Start with patient module tests, then add doctor, appointment, billing tests.
- Add a `pytest.ini` and sample test command.

## 3.4 Security and Access Control

### Deliverables

- Implement JWT authentication.
- Add route dependencies to enforce roles.
- Protect patient, doctor, billing, and inventory endpoints.
- Add password hashing and token expiry.

## 3.5 Deployment and Container Improvements

### Deliverables

- Add `Dockerfile.prod` or multi-stage production build.
- Add environment variable config support using `python-dotenv` and `pydantic-settings`.
- Add `docker-compose.override.yml` for local development.
- Add health checks on the API container.

## 3.6 Documentation and API Reference

### Deliverables

- Add `README.md` with setup and run instructions.
- Add `API.md` describing routes, schemas, and auth flow.
- Add a `docs/` folder if needed.

---

# Phase 4 — Python Frontend User Interface

This project should keep the frontend within the Python ecosystem. The best approach is a server-rendered UI built on the same backend framework rather than a separate JavaScript SPA.

## 4.1 Frontend architecture

- Use FastAPI with `Jinja2` templates or a compatible Python templating engine.
- Create `app/templates/` for HTML pages and `app/static/` for CSS, images, and minimal JavaScript.
- Use server-side page generation for key workflows, then add progressive enhancement with HTMX-style interactions if needed.
- Keep UI logic in Python services and route handlers while the templates render data and forms.

## 4.2 Best frontend stack

- FastAPI + Jinja2 for page rendering and form handling.
- `python-multipart` for form uploads and file handling.
- Optional lightweight Python UI tools like `panel`, `streamlit`, or `anvil` only if a separate admin dashboard is needed, but prefer integrated FastAPI templates first.
- Avoid React/Vue/Angular; instead, use Python templating plus minimal JavaScript for interactivity.

## 4.3 UI pages and user experience

- `login.html` / `register.html` for authentication.
- `dashboard.html` for a staff/admin overview.
- `patients/list.html`, `patients/detail.html`, and `patients/form.html`.
- `doctors/list.html`, `appointments/list.html`, and `appointments/form.html`.
- `billing/invoices.html`, `billing/payments.html`, `insurance/coverage-warnings.html`, and `inventory/list.html`.
- `reports/dashboard.html` for analytics and operational KPIs.

## 4.4 Developer workflow

- Build UI pages incrementally alongside API routes.
- Render server-side HTML for every major entity first.
- Add modern interaction only when needed, using small Python-friendly patterns.
- Keep the frontend maintainable by avoiding large JavaScript codebases.

---

# Detailed Implementation Plan by Module

## Module: Authentication and Users

### New files

- `app/models/user.py`
- `app/schemas/user.py`
- `app/services/auth.py`
- `app/routers/auth.py`
- `app/auth/security.py`
- `app/auth/__init__.py`

### Core concepts

- `User` stores username, email, hashed password, role, and status.
- `Role` values control what each user can do.
- `JWT` tokens authorize API access.
- `Depends(get_current_user)` protects routes.

### Important workflows

- Registration: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/token`
- Token refresh and validation.

## Module: Patient Management

### Current scope

- `app/models/patient.py`
- `app/schemas/patient.py`
- `app/services/patient.py`
- `app/routers/patient.py`

### Enhancements

- add more patient fields
- add search API by name / email / phone
- add patient history endpoint
- add soft delete using `is_active`

### Example routes

- `GET /api/v1/patients/search`
- `GET /api/v1/patients/{id}/history`
- `PATCH /api/v1/patients/{id}/toggle-active`

## Module: Doctor and Staff Management

### New files

- `app/models/doctor.py`
- `app/models/staff.py`
- `app/schemas/doctor.py`
- `app/schemas/staff.py`
- `app/services/doctor.py`
- `app/services/staff.py`
- `app/routers/doctor.py`
- `app/routers/staff.py`

### Important relationships

- Doctor has many Appointments.
- Staff may support scheduling and billing tasks.

### Use cases

- Create doctor profile
- Update doctor availability
- List departments and specialties

## Module: Appointments

### New files

- `app/models/appointment.py`
- `app/schemas/appointment.py`
- `app/services/appointment.py`
- `app/routers/appointment.py`

### Business rules

- Enforce appointment time conflicts at doctor-level.
- Support appointment status transitions.
- Allow reschedule and cancellation.

### Example endpoints

- `POST /api/v1/appointments`
- `GET /api/v1/appointments?doctor_id=&date=`
- `PUT /api/v1/appointments/{id}`
- `DELETE /api/v1/appointments/{id}`

## Module: Encounters and Records

### New files

- `app/models/medical_record.py`
- `app/schemas/medical_record.py`
- `app/services/medical_record.py`
- `app/routers/medical_record.py`

### Use cases

- Store encounter notes after appointment completion
- Query patient record history
- Attach diagnoses and treatment plans

## Module: Billing and Payments

### New files

- `app/models/invoice.py`
- `app/models/payment.py`
- `app/models/billing_line_item.py`
- `app/schemas/invoice.py`
- `app/schemas/payment.py`
- `app/services/billing.py`
- `app/routers/billing.py`

### Key features

- Generate invoices automatically after appointment completion.
- Allow payment capture with multiple methods.
- Support invoice search and payment reconciliation.

## Module: Insurance Optimization and Claims Validation

### New files

- `app/models/insurance_policy.py`
- `app/models/coverage_review.py`
- `app/schemas/insurance_policy.py`
- `app/schemas/coverage_review.py`
- `app/services/insurance.py`
- `app/routers/insurance.py`

### Key features

- Extract insurance coverage rules from uploaded policy text.
- Validate upcoming appointments against insurance policy constraints.
- Flag potential claim denials before the patient visits the hospital.
- Provide patient-facing and staff-facing warnings for coverage gaps and pre-authorization needs.

### Design notes

- Use a free, rule-based or open-source text extraction pipeline for policy clauses, rather than paid RAG APIs.
- Store key terms in `InsurancePolicy` so coverage decisions are repeatable and auditable.
- Link coverage reviews to appointments, patients, and providers.

## Module: Inventory and Pharmacy

### New files

- `app/models/inventory_item.py`
- `app/models/prescription.py`
- `app/models/stock_transaction.py`
- `app/schemas/inventory_item.py`
- `app/schemas/prescription.py`
- `app/services/inventory.py`
- `app/routers/inventory.py`

### Business rules

- Track medication stock levels.
- Record dispensed medications.
- Manage reorder alerts and supplier orders.

---

# Database and Migration Strategy

## Database design principles

- Normalize data so each table represents one real-world entity.
- Use foreign keys to enforce relationships.
- Use indexes on search and join columns.
- Keep audit fields on every major table: `created_at`, `updated_at`, `created_by`, `updated_by`.

## Alembic workflow

- Use `alembic revision --autogenerate -m "<message>"` after each schema change.
- Use a separate `env.py` database URL configuration if needed.
- Commit migrations alongside model changes.

## Recommended tables

- `users`
- `patients`
- `doctors`
- `staff`
- `appointments`
- `medical_records`
- `invoices`
- `billing_line_items`
- `payments`
- `insurance_policies`
- `coverage_reviews`
- `inventory_items`
- `prescriptions`
- `stock_transactions`
- `audit_logs`

---

# Testing Plan

## Testing goals

- validate business logic without the UI
- guard major modules from regressions
- catch broken database migrations early

## Test layers

1. Unit tests for services
2. Router tests for API contract
3. Integration tests for DB behavior

## Suggested structure

- `tests/`
  - `tests/test_patient_service.py`
  - `tests/test_patient_router.py`
  - `tests/test_auth.py`
  - `tests/test_appointment.py`
  - `tests/test_billing.py`

## Tools

- `pytest`
- `httpx` for API calls in tests
- `factory_boy` or simple builder helpers for fixtures

## Example commands

- `pytest tests/`
- `docker compose run api pytest tests/`

---

# Development Workflow

## Local development with Docker

1. Create `.env` with Postgres settings.
2. Run `docker compose up --build`.
3. Visit `http://localhost:8000/docs` for Swagger.
4. Run migrations inside `api` container if needed.
5. Use Python-based UI pages via the API service, not a separate JS frontend.

## Recommended command file updates

Add commands to `commands.md` such as:

- `docker compose up --build`
- `docker compose exec api alembic upgrade head`
- `docker compose exec api pytest`

## Version control

- Use feature branches for each major module.
- Keep migrations and model changes together.
- Write small PR-sized increments.

---

# Roadmap and Milestones

## Milestone 1 — ERP Core API

- Complete patient CRUD and search.
- Add authentication and user roles.
- Add doctor/staff CRUD.
- Add appointment scheduling.
- Add basic medical encounter notes.
- Add Alembic migrations.

## Milestone 2 — Billing and Pharmacy

- Add invoices and payments.
- Add inventory tracking and prescriptions.
- Add role-based billing access.
- Add test coverage for financial flows.

## Milestone 3 — UX and Production Readiness

- Add frontend app or simple admin UI.
- Add logging, monitoring, and audit trails.
- Add production container build and deployment docs.
- Add full API documentation.

## Milestone 4 — Extended Hospital Operations

- Add laboratory orders and results.
- Add appointment reminders / notifications.
- Add analytics dashboards.
- Optimize queries and add caching if needed.

---

# Appendix: File Map for Full ERP

## App structure after full ERP

- `app/main.py`
- `app/auth/`
  - `security.py`
  - `__init__.py`
- `app/database/`
  - `database.py`
- `app/models/`
  - `base.py`
  - `patient.py`
  - `doctor.py`
  - `staff.py`
  - `appointment.py`
  - `medical_record.py`
  - `user.py`
  - `invoice.py`
  - `payment.py`
  - `billing_line_item.py`
  - `insurance_policy.py`
  - `coverage_review.py`
  - `inventory_item.py`
  - `prescription.py`
  - `stock_transaction.py`
  - `audit_log.py`
- `app/schemas/`
  - `patient.py`
  - `doctor.py`
  - `staff.py`
  - `appointment.py`
  - `medical_record.py`
  - `user.py`
  - `invoice.py`
  - `payment.py`
  - `insurance_policy.py`
  - `coverage_review.py`
  - `inventory_item.py`
  - `prescription.py`
- `app/services/`
  - `patient.py`
  - `doctor.py`
  - `appointment.py`
  - `medical_record.py`
  - `auth.py`
  - `billing.py`
  - `insurance.py`
  - `inventory.py`
- `app/routers/`
  - `patient.py`
  - `doctor.py`
  - `staff.py`
  - `appointment.py`
  - `medical_record.py`
  - `auth.py`
  - `billing.py`
  - `insurance.py`
  - `inventory.py`
- `app/templates/`
- `app/static/`
- `app/utils/`
  - `exceptions.py`
  - `pagination.py`
  - `logging.py`

---

# Notes for execution

This plan is intentionally incremental. Start with core clinical modules and do not branch into billing or inventory until the clinical data model is stable.

When you implement a module:

- add models first
- then add schemas
- then add services
- then add routers
- then add migrations
- then add tests

That order preserves the architecture and minimizes rework.
