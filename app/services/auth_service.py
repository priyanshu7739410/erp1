from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.hashing import get_password_hash, verify_password
from app.auth.jwt_handler import create_access_token
from app.utils.exceptions import ConflictException, UnauthorizedException

def register_user(db: Session, user_data: UserCreate) -> User:
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise ConflictException(detail="Username or email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role or "receptionist",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username: str, password: str) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException(detail="Incorrect username or password")
    if not user.is_active:
        raise UnauthorizedException(detail="Account is inactive")
    
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
