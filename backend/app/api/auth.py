"""
Authentication & User Account API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.app.schemas.auth_schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from backend.app.services.email_service import email_service
from database.models import User
import re
import random
import time
from typing import Dict, Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory OTP storage for password resets: user_id -> {"otp": "...", "expires_at": float}
OTP_STORE: Dict[int, Dict[str, Any]] = {}

def find_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """Helper to locate a user by Email or Phone number (with fuzzy digits matching)."""
    clean_id = (identifier or "").strip()
    if not clean_id:
        return None

    # 1. Search by email (case-insensitive)
    user = db.query(User).filter(User.email == clean_id.lower()).first()
    if user:
        return user

    # 2. Search by exact phone
    user = db.query(User).filter(User.phone == clean_id).first()
    if user:
        return user

    # 3. Search by normalized phone digits (e.g., 9876543210 vs +91-9876543210)
    input_digits = re.sub(r"\D", "", clean_id)
    if len(input_digits) >= 10:
        last10 = input_digits[-10:]
        for candidate in db.query(User).all():
            cand_digits = re.sub(r"\D", "", candidate.phone or "")
            if cand_digits.endswith(last10):
                return candidate

    return None

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

@router.post("/login", response_model=TokenResponse, summary="Log in with email or phone number and password")
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)) -> Any:
    login_id = (payload.identifier or payload.email or "").strip()
    if not login_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide an email address or phone number."
        )

    user = find_user_by_identifier(db, login_id)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone number or password",
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

@router.post("/forgot-password", summary="Request a password reset verification code")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> Any:
    user = find_user_by_identifier(db, payload.identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address or phone number."
        )

    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    OTP_STORE[user.id] = {
        "otp": otp,
        "expires_at": time.time() + 900  # 15 minutes
    }

    # Dispatch email if user has an email address
    email_dispatch = {"sent": False}
    if user.email:
        email_dispatch = email_service.send_otp_email(
            to_email=user.email,
            user_name=user.name,
            otp_code=otp
        )

    target_display = user.email if "@" in payload.identifier else user.phone
    is_real_sent = bool(email_dispatch.get("sent"))

    return {
        "success": True,
        "message": (
            f"Verification code has been sent directly to your email ({user.email})."
            if is_real_sent
            else f"Verification code generated for {target_display}."
        ),
        "email_sent": is_real_sent,
        "demo_otp": otp if not is_real_sent else None, # Only display demo OTP if real email was not sent
        "user_name": user.name,
        "expires_in_minutes": 15
    }

@router.post("/reset-password", summary="Reset password using OTP code")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> Any:
    user = find_user_by_identifier(db, payload.identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address or phone number."
        )

    # Validate OTP (allows generated OTP or standard 123456 demo code)
    stored = OTP_STORE.get(user.id)
    otp_valid = False
    clean_otp = payload.otp.strip()

    if clean_otp == "123456":
        otp_valid = True
    elif stored and stored.get("otp") == clean_otp:
        if time.time() <= stored.get("expires_at", 0):
            otp_valid = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check and try again."
        )

    # Update password
    user.password_hash = hash_password(payload.new_password)
    db.commit()

    # Clear OTP
    OTP_STORE.pop(user.id, None)

    return {
        "success": True,
        "message": "Password reset successfully. You can now sign in with your new password."
    }

@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
    return current_user
