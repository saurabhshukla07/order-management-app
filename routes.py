"""
API Routes for Order Management System
Defines all API endpoints for authentication and order management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from database import get_db
from models import User, Order, OrderStatus
from schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    OrderCreate, OrderResponse, OrderListResponse, MessageResponse
)
from auth import hash_password, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# ============ Authentication Routes ============

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    - Validates email uniqueness
    - Hashes password before storing
    - Returns created user information
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    return new_user

@router.post("/auth/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    - Validates email and password
    - Generates JWT token valid for 15 minutes
    - Returns access token
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Login failed for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token with user email as subject
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    }

# ============ Order Routes ============

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order for authenticated user
    - Requires valid JWT token
    - Order starts with 'pending' status
    - Returns created order information
    """
    # Create new order associated with current user
    new_order = Order(
        user_id=current_user.id,
        product_name=order_data.product_name,
        amount=order_data.amount,
        status=OrderStatus.PENDING
    )
    
    # Save to database
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    logger.info(f"Order created: ID={new_order.id}, User={current_user.email}, Product={order_data.product_name}")
    return new_order

@router.get("/orders", response_model=OrderListResponse)
def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for authenticated user
    - Requires valid JWT token
    - Returns list of orders with total count
    - Orders sorted by creation date (newest first)
    """
    # Query all orders for current user
    orders = db.query(Order)\
        .filter(Order.user_id == current_user.id)\
        .order_by(Order.created_at.desc())\
        .all()
    
    logger.info(f"Orders retrieved: {len(orders)} orders for user {current_user.email}")
    return {
        "orders": orders,
        "total": len(orders)
    }

@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order if it's still pending
    - Requires valid JWT token
    - User can only cancel their own orders
    - Only 'pending' orders can be cancelled
    - Returns updated order information
    """
    # Find order by ID
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # Check if order exists
    if not order:
        logger.warning(f"Cancel failed: Order {order_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if order belongs to current user
    if order.user_id != current_user.id:
        logger.warning(f"Cancel failed: User {current_user.email} attempted to cancel order {order_id} of another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own orders"
        )
    
    # Check if order is still pending
    if order.status != OrderStatus.PENDING:
        logger.warning(f"Cancel failed: Order {order_id} status is {order.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    # Update order status to cancelled
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order cancelled: ID={order_id}, User={current_user.email}")
    return order