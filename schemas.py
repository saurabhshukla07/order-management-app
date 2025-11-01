"""
Pydantic schemas for request/response validation
Defines data models for API input and output
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from models import OrderStatus

# ============ Authentication Schemas ============

class UserRegister(BaseModel):
    """Schema for user registration request"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")

class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")

class UserResponse(BaseModel):
    """Schema for user information response"""
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows creation from ORM models

# ============ Order Schemas ============

class OrderCreate(BaseModel):
    """Schema for creating a new order"""
    product_name: str = Field(..., min_length=1, max_length=200, description="Name of the product")
    amount: float = Field(..., gt=0, description="Order amount (must be positive)")

class OrderResponse(BaseModel):
    """Schema for order information response"""
    id: int
    user_id: int
    product_name: str
    amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows creation from ORM models

class OrderListResponse(BaseModel):
    """Schema for list of orders response"""
    orders: list[OrderResponse]
    total: int = Field(..., description="Total number of orders")

# ============ Generic Schemas ============

class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str = Field(..., description="Response message")

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error description")