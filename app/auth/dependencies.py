from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.jwt_handler import decode_access_token
from app.models.user import User
from app.utils.exceptions import UnauthorizedException, ForbiddenException
from typing import List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException(detail="Invalid or expired authentication token")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise UnauthorizedException(detail="User not found")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user account")
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles and user.role != "admin":
            raise ForbiddenException(detail=f"Operation not permitted for role: {user.role}")
        return user
