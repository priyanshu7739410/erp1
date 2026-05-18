# MediCloud Hospital ERP

MediCloud is a robust, full-scale Enterprise Resource Planning (ERP) platform designed for modern healthcare facilities. Built with an autonomous, resilient architecture on FastAPI and SQLAlchemy, it seamlessly bridges clinical operations, financial billing, insurance optimization, and pharmaceutical inventory control.

## System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Web UI & API Layer                   │
│        (FastAPI / Jinja2 Templates / OpenAPI)          │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  Domain Service Layer                  │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Auth & Users    │  │  Patient CRUD    │            │
│  ├──────────────────┤  ├──────────────────┤            │
│  │ Doctor & Staff   │  │ Appointments     │            │
│  ├──────────────────┤  ├──────────────────┤            │
│  │ Medical Records  │  │ Billing & Pay    │            │
│  ├──────────────────┤  ├──────────────────┤            │
│  │ Insurance NLP    │  │ Pharmacy Stock   │            │
│  └──────────────────┘  └──────────────────┘            │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                    Database Layer                      │
│             (SQLAlchemy ORM / SQLite / PG)             │
└────────────────────────────────────────────────────────┘
```

## Features & Functional Modules

1. **Authentication & Role-Based Access Control (RBAC)**
   - Secure Argon2 password hashing.
   - JWT authentication.
   - Differentiated access roles: `admin`, `doctor`, `receptionist`, `nurse`, `pharmacist`, `billing_officer`.
2. **Clinical Management**
   - Full patient registration, demographics, emergency contacts, and clinical histories.
   - Doctor, department, and medical staff scheduling.
   - Conflict-free appointment booking with capacity constraints.
   - Encounter recording, diagnosis, and care plan tracking.
3. **Financial Billing & Invoicing**
   - Automated invoice generation upon clinical encounter completion.
   - Granular charge tracking and line-item breakdowns.
   - Flexible payment capture (Cash, Card, Bank Transfer, Insurance) with automatic status recalculation (`pending`, `partially_paid`, `paid`).
4. **Insurance Optimization & Pre-Authorization**
   - Free, local rule-based NLP extraction engine to parse uploaded insurance policy documents.
   - Automated pre-appointment coverage reviews to flag out-of-network risks, policy exclusions, and calculate estimated patient out-of-pocket costs.
5. **Pharmacy & Inventory Control**
   - Inventory cataloging with SKUs, categories, and stock level tracking.
   - Automatic reorder alerts when stock drops below minimum thresholds.
   - E-prescription writing and automated pharmacy dispensing that dynamically updates stock levels.
   - Supplier purchase order creation and receiving.
6. **Audit Trails & Monitoring**
   - Automated audit logging for key actions across entities (`CREATE`, `UPDATE`, `DELETE`).
   - Request timing and middleware tracing.
7. **Premium Server-Rendered Web Interface**
   - Beautiful, rich dark-mode UI with sleek glassmorphism, responsive navigation, and intuitive operational dashboards.

## Quick Start & Running Locally

### 1. Local Environment Setup
Ensure Python 3.10+ is installed.
```bash
# Clone the repository and navigate to the project directory
cd erp1

# Install curated development dependencies
pip install -r requirements/dev.txt
```

### 2. Database Migrations
Initialize the SQLite/PostgreSQL schema using Alembic:
```bash
alembic upgrade head
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Web UI**: Visit [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
- **Default Login**: Username: `admin`, Password: `admin123`

### 4. Running via Docker Compose
To run the full stack (API + PostgreSQL containerized):
```bash
docker compose up --build
```

### 5. Running Automated Tests
```bash
pytest
```