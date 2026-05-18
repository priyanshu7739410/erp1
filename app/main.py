from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.routers import (
    auth, patient, department, doctor, staff, appointment,
    medical_record, billing, insurance, inventory, audit, web
)
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException, UnauthorizedException, ConflictException

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        # In a production setting, log process_time and request details
        return response

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.utils.limiter import limiter

app = FastAPI(
    title="MediCloud Hospital ERP",
    description="Full-scale production Enterprise Resource Planning system for healthcare facilities.",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LoggingMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    return RedirectResponse(url=f"/?error={exc.detail}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )

# Include API Routers
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(department.router)
app.include_router(doctor.router)
app.include_router(staff.router)
app.include_router(appointment.router)
app.include_router(medical_record.router)
app.include_router(billing.router)
app.include_router(insurance.router)
app.include_router(inventory.router)
app.include_router(audit.router)

# Include Web UI Router
app.include_router(web.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": time.time()}