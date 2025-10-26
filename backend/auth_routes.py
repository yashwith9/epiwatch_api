"""
Authentication Routes for EpiWatch API
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

try:
    from backend.database import get_db
    from backend.models import User
    from backend.schemas import (
        SignUpRequest, 
        LoginRequest, 
        AuthResponse, 
        UserResponse,
        TokenValidationResponse
    )
    from backend.auth_utils import (
        hash_password, 
        verify_password, 
        create_access_token, 
        decode_token
    )
except ImportError:
    from database import get_db
    from models import User
    from schemas import (
        SignUpRequest, 
        LoginRequest, 
        AuthResponse, 
        UserResponse,
        TokenValidationResponse
    )
    from auth_utils import (
        hash_password, 
        verify_password, 
        create_access_token, 
        decode_token
    )

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **fullName**: User's full name (required)
    - **email**: User's email address (required, must be unique)
    - **organization**: Organization name (optional)
    - **password**: Password with minimum 6 characters (required)
    - **confirmPassword**: Password confirmation (must match password)
    
    Returns:
        - JWT token
        - User information
        - Success message
    
    Raises:
        - 400: Bad request (validation errors)
        - 409: Conflict (email already exists)
        - 500: Server error
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Please use a different email or login."
            )
        
        # Hash the password
        hashed_pwd = hash_password(request.password)
        
        # Create new user
        new_user = User(
            full_name=request.fullName,
            email=request.email,
            organization=request.organization,
            hashed_password=hashed_pwd,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate JWT token
        token_data = {
            "sub": new_user.email,
            "user_id": new_user.id
        }
        access_token = create_access_token(data=token_data)
        
        # Prepare response
        user_response = UserResponse(
            id=new_user.id,
            fullName=new_user.full_name,
            email=new_user.email,
            organization=new_user.organization,
            createdAt=new_user.created_at.isoformat()
        )
        
        return AuthResponse(
            token=access_token,
            user=user_response,
            message="Account created successfully! Welcome to EpiWatch."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return token
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns:
        - JWT token
        - User information
        - Success message
    
    Raises:
        - 401: Unauthorized (invalid credentials)
        - 500: Server error
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password. Please check your credentials."
            )
        
        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password. Please check your credentials."
            )
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate JWT token
        token_data = {
            "sub": user.email,
            "user_id": user.id
        }
        access_token = create_access_token(data=token_data)
        
        # Prepare response
        user_response = UserResponse(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            organization=user.organization,
            createdAt=user.created_at.isoformat()
        )
        
        return AuthResponse(
            token=access_token,
            user=user_response,
            message="Login successful! Welcome back to EpiWatch."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.get("/validate", response_model=TokenValidationResponse)
async def validate_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Validate JWT token from Authorization header
    
    - **Authorization**: Bearer token in header (format: "Bearer <token>")
    
    Returns:
        - valid: Boolean indicating if token is valid
        - user: User information if token is valid
    
    Raises:
        - 401: Unauthorized (invalid or missing token)
    """
    try:
        # Check if Authorization header exists
        if not authorization:
            return TokenValidationResponse(valid=False, user=None)
        
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return TokenValidationResponse(valid=False, user=None)
        
        token = parts[1]
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return TokenValidationResponse(valid=False, user=None)
        
        # Get user email from token
        email = payload.get("sub")
        if not email:
            return TokenValidationResponse(valid=False, user=None)
        
        # Find user in database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return TokenValidationResponse(valid=False, user=None)
        
        # Prepare user response
        user_response = UserResponse(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            organization=user.organization,
            createdAt=user.created_at.isoformat()
        )
        
        return TokenValidationResponse(valid=True, user=user_response)
        
    except Exception as e:
        return TokenValidationResponse(valid=False, user=None)
