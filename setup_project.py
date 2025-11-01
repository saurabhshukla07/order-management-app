"""
Project Setup Script
Run this script to automatically create all project files
Usage: python setup_project.py
"""

import os

def create_file(filename, content):
    """Create a file with given content"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {filename}")

def setup_project():
    """Create all project files"""
    print("🚀 Setting up Order Management API project...\n")
    
    # Create requirements.txt
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
apscheduler==3.10.4
pydantic==2.5.0
pydantic-settings==2.1.0
python-dateutil==2.8.2
"""
    create_file('requirements.txt', requirements)
    
    # Create .env.example
    env_example = """DATABASE_URL=postgresql://postgres:password@localhost:5432/order_management
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
APP_HOST=0.0.0.0
APP_PORT=8000
"""
    create_file('.env.example', env_example)
    
    # Create models.py
    models = '''"""
Database models for Order Management System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
'''
    create_file('models.py', models)
    
    # Create database.py
    database = '''"""
Database configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/order_management")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
'''
    create_file('database.py', database)
    
    # Create auth.py
    auth = '''"""
Authentication utilities
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database import get_db
from models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    email: str = payload.get("sub")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
'''
    create_file('auth.py', auth)
    
    # Create schemas.py
    schemas = '''"""
Pydantic schemas for validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models import OrderStatus

class UserRegister(BaseModel):
    """User registration schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    """Order creation schema"""
    product_name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)

class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    user_id: int
    product_name: str
    amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """Order list response"""
    orders: list[OrderResponse]
    total: int
'''
    create_file('schemas.py', schemas)
    
    # Create routes.py
    routes = '''"""
API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from database import get_db
from models import User, Order, OrderStatus
from schemas import UserRegister, UserLogin, Token, UserResponse, OrderCreate, OrderResponse, OrderListResponse
from auth import hash_password, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {new_user.email}")
    return new_user

@router.post("/auth/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES}

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new order"""
    new_order = Order(
        user_id=current_user.id,
        product_name=order_data.product_name,
        amount=order_data.amount,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    logger.info(f"Order created: ID={new_order.id}, User={current_user.email}")
    return new_order

@router.get("/orders", response_model=OrderListResponse)
def get_user_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return {"orders": orders, "total": len(orders)}

@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cancel order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel order with status: {order.status}")
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    logger.info(f"Order cancelled: ID={order_id}")
    return order
'''
    create_file('routes.py', routes)
    
    # Create background_jobs.py
    background = '''"""
Background job scheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import SessionLocal
from models import Order, OrderStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pending_orders():
    """Process pending orders"""
    db: Session = SessionLocal()
    try:
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).all()
        if not pending_orders:
            logger.info(f"[{datetime.utcnow()}] No pending orders")
            return
        
        logger.info(f"[{datetime.utcnow()}] Processing {len(pending_orders)} orders")
        for order in pending_orders:
            order.status = OrderStatus.PROCESSING
            db.commit()
            logger.info(f"  → Order #{order.id} - PROCESSING")
            
            order.status = OrderStatus.COMPLETED
            db.commit()
            logger.info(f"  ✓ Order #{order.id} - COMPLETED")
        
        logger.info(f"[{datetime.utcnow()}] Processed {len(pending_orders)} orders")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Start background scheduler"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_pending_orders, 'interval', seconds=120, id='process_orders')
    scheduler.start()
    logger.info("✓ Background scheduler started (every 2 minutes)")
    return scheduler
'''
    create_file('background_jobs.py', background)
    
    # Create main.py
    main = '''"""
Main FastAPI application
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from database import init_db
from routes import router
from background_jobs import start_scheduler

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("🚀 Starting Order Management API...")
    init_db()
    start_scheduler()
    logger.info("✓ Startup complete")
    yield
    logger.info("🛑 Shutting down...")

app = FastAPI(
    title="Order Management API",
    description="Backend API for managing orders",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, tags=["API"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = [f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()]
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Validation error", "errors": errors})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions"""
    logger.error(f"Error: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})

@app.get("/", tags=["Health"])
def health_check():
    """Health check"""
    return {"status": "healthy", "message": "Order Management API is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
'''
    create_file('main.py', main)
    
    print("\n✅ All files created successfully!")
    print("\n📋 Next steps:")
    print("1. cp .env.example .env")
    print("2. Edit .env with your database credentials")
    print("3. pip install -r requirements.txt")
    print("4. python main.py")

if __name__ == "__main__":
    setup_project()