"""
Pydantic Schemas for Authentication
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    """Schema for user registration"""
    fullName: str = Field(..., min_length=2, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    organization: Optional[str] = Field(None, max_length=255, description="Organization name")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    confirmPassword: str = Field(..., description="Password confirmation")
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for user information in response"""
    id: int
    fullName: str
    email: str
    organization: Optional[str]
    createdAt: str
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    token: str = Field(..., description="JWT authentication token")
    user: UserResponse
    message: str = Field(..., description="Success message")


class TokenValidationResponse(BaseModel):
    """Schema for token validation response"""
    valid: bool = Field(..., description="Whether token is valid")
    user: Optional[UserResponse] = Field(None, description="User information if token is valid")
