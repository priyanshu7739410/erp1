# MediCloud ERP — Comprehensive Operational Commands Reference

This document provides detailed CLI commands for managing, migrating, testing, debugging, and deploying the MediCloud Hospital ERP system across local and containerized environments.

---

## 1. Local Environment & Dependency Management

### Virtual Environment Setup
```bash
# Create a new Python virtual environment
python -m venv venv

# Activate on Windows (PowerShell / Command Prompt)
.\venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

### Managing Curated Packages
To maintain a clean, anti-drift architecture, dependencies are strictly modularized under `requirements/`. Never use `pip freeze > requirements.txt`.

```bash
# Install core backend production dependencies
pip install -r requirements/base.txt

# Install complete development and testing tooling
pip install -r requirements/dev.txt

# Install optional analytics/ML tools
pip install -r requirements/data.txt
```

---

## 2. Docker & Docker Compose Operations

### Starting and Stopping Services
```bash
# Build and start all services in the background (detached mode)
docker compose up -d --build

# Start services in foreground with real-time aggregated log output
docker compose up --build

# Stop and gracefully shut down all running containers
docker compose down

# Stop containers and destroy associated named volumes (WARNING: Resets PostgreSQL database)
docker compose down -v
```

### Container Inspection & Monitoring
```bash
# List all running ERP containers and their port mappings/health status
docker compose ps

# View live trailing logs for all services
docker compose logs -f

# View live trailing logs specifically for the FastAPI backend
docker compose logs -f api

# View live trailing logs specifically for PostgreSQL
docker compose logs -f db
```

### Executing Commands Inside Containers
```bash
# Open an interactive Bash shell inside the running API container
docker compose exec api /bin/bash

# Open an interactive PostgreSQL CLI session inside the database container
docker compose exec db psql -U erp_user -d hospital_erp

# Run Alembic migrations inside the running API container
docker compose exec api alembic upgrade head

# Run unit tests inside the running API container
docker compose exec api pytest -v
```

### Docker System Maintenance
```bash
# Remove dangling images, unused networks, and build cache
docker system prune -f

# Remove all unused volumes
docker volume prune -f
```

---

## 3. Database Schema & Alembic Migrations

### Generating Migrations
```bash
# Autogenerate a new migration revision based on changes made in app/models/
alembic revision --autogenerate -m "Add new fields to patient model"

# (Fallback) If alembic binary is not in PATH, execute via Python:
python -c "import sys; from alembic.config import main; sys.exit(main())" revision --autogenerate -m "Add new fields to patient model"
```

### Applying & Reverting Migrations
```bash
# Upgrade database schema to the latest head revision
alembic upgrade head

# Upgrade schema up to a specific revision ID (e.g. 7ae45fc043d6)
alembic upgrade 7ae45fc043d6

# Downgrade schema by exactly one revision
alembic downgrade -1

# Downgrade schema back to an entirely clean, empty database state
alembic downgrade base

# View existing migration history and current head status
alembic history --verbose
alembic current
```

---

## 4. Running Server Locally (Without Docker)

### Starting the FastAPI Backend
```bash
# Run server with hot-reload enabled for local development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run server with multiple workers (production-grade simulation)
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Key Application URLs
- **Web Portal / UI**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger / OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 5. Automated Testing Suite (`pytest`)

### Running Tests
```bash
# Run the complete test suite across all modules
pytest

# Run tests with detailed pass/fail output and duration timings
pytest -v

# Run tests and print standard output (e.g., print statements inside tests)
pytest -s
```

### Targeted & Filtered Testing
```bash
# Run tests specifically within a single test file
pytest tests/test_patient.py -v

# Run a specific test function by name substring match
pytest -k "test_create_appointment or test_login_success" -v

# Exit immediately upon encountering the first test failure
pytest -x
```

---

## 6. Administrative Scripting & Seeding

### Seeding Default Administrator Account
If starting from a fresh database instance, you can manually seed the default admin account (`admin` / `admin123`):
```bash
python -c "from app.database.session import SessionLocal; from app.models.user import User; from app.auth.hashing import get_password_hash; db = SessionLocal(); u = db.query(User).filter_by(username='admin').first(); (db.add(User(username='admin', email='admin@hospital.erp', hashed_password=get_password_hash('admin123'), role='admin', is_active=True)) if not u else None); db.commit(); print('Admin user successfully verified/seeded.')"
```
