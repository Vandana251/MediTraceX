"""
Authentication & User Account API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.app.schemas.auth_schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Register a new customer or pharmacy account")
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> Any:
    # Check duplicate email
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )
    
    # Check duplicate phone
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists."
        )

    # Normalize role
    role = payload.role.lower() if payload.role else "customer"
    if role not in ["customer", "pharmacy_admin", "pharmacy", "system_admin"]:
        role = "customer"
    if role == "pharmacy":
        role = "pharmacy_admin"

    new_user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip(),
        password_hash=hash_password(payload.password),
        role=role,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }

@router.post("/login", response_model=TokenResponse, summary="Log in with email and password")
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
    return current_user
