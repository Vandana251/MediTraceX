"""
Pydantic Schemas for Authentication & User Accounts
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Full Name of the user")
    email: str = Field(..., description="Unique user email address")
    phone: str = Field(..., min_length=8, max_length=20, description="Contact phone number")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    role: str = Field(default="customer", description="Role: 'customer' or 'pharmacy_admin'")
    latitude: Optional[float] = Field(default=None, description="User home/current latitude")
    longitude: Optional[float] = Field(default=None, description="User home/current longitude")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format")
        return v

class UserLoginRequest(BaseModel):
    email: Optional[str] = Field(default=None, description="Registered email address or phone number")
    identifier: Optional[str] = Field(default=None, description="Registered email address or phone number")
    password: str = Field(..., description="Account password")

    @field_validator("email", "identifier")
    @classmethod
    def clean_identifier(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Registered email address or phone number")

    @field_validator("identifier")
    @classmethod
    def clean_identifier(cls, v: str) -> str:
        return v.strip()

class ResetPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Registered email address or phone number")
    otp: str = Field(..., min_length=4, max_length=10, description="Verification OTP code")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)")

    @field_validator("identifier", "otp", "new_password")
    @classmethod
    def clean_fields(cls, v: str) -> str:
        return v.strip()
