# Changelog

All notable changes to the MediCloud Hospital ERP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-18
### Added
- **Authentication & RBAC:** Argon2 password hashing, JWT token authentication, and multi-role access control (Admin, Doctor, Patient, Nurse, Receptionist, Pharmacist, Billing Officer).
- **Core Clinical Domain:** Full patient registration, physician profiling, appointment conflict management, and encounter charting.
- **Financial & Billing:** Automated invoice generation upon appointment completion, itemized charge tracking, and multi-method payment capture.
- **Insurance Optimization:** Automated NLP-based text parser to analyze policy terms, calculate deductibles, and pre-verify appointment coverage.
- **Pharmacy & Inventory:** Stock tracking, automated reorder threshold alerts, supplier purchase orders, and secure digital e-prescribing.
- **Web UI:** Responsive Jinja2 templates with role-tailored dashboards (`dashboard_patient.html`, `dashboard_doctor.html`) and navigation menus.
- **Security:** SlowAPI rate-limiting middleware (120 req/min default, 5 req/min on auth endpoints).
- **CI/CD:** Automated GitHub Actions test pipeline (`.github/workflows/ci.yml`).

### Security
- Removed exposed PostgreSQL port `5432` from public host binding in Docker Compose.
- Isolated all environment variables and database passwords into gitignored `.env` file.
- Added idempotency safety checks to database seeding script.
