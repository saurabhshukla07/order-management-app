"""
Main FastAPI application entry point
Initializes the application, database, and background jobs
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

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup: Initialize database and background jobs
    logger.info("🚀 Starting Order Management API...")
    init_db()
    start_scheduler()
    logger.info("✓ Application startup complete")
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("🛑 Shutting down application...")

# Create FastAPI application instance
app = FastAPI(
    title="Order Management API",
    description="Backend API for managing orders with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router, tags=["API"])

# ============ Exception Handlers ============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from Pydantic
    Returns user-friendly error messages with 400 status
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error", "errors": errors}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    Returns 500 Internal Server Error
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# ============ Health Check Endpoint ============

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint
    Returns API status and version
    """
    return {
        "status": "healthy",
        "message": "Order Management API is running",
        "version": "1.0.0"
    }

# Run application with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True  # Enable auto-reload during development
    )