from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_data)

@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = authenticate_user(db, form_data.username, form_data.password)
    return {"access_token": result["access_token"], "token_type": result["token_type"]}
