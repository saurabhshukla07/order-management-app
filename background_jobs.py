"""
Background job scheduler for processing orders
Runs every 2-3 minutes to process pending orders
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import SessionLocal
from models import Order, OrderStatus

# Setup logging for background jobs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pending_orders():
    """
    Background job to process pending orders
    - Runs every 2-3 minutes
    - Finds all orders with 'pending' status
    - Updates them to 'processing' then 'completed'
    - Logs all processed orders
    """
    # Create a new database session for this job
    db: Session = SessionLocal()
    
    try:
        # Find all pending orders
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).all()
        
        if not pending_orders:
            logger.info(f"[{datetime.utcnow()}] No pending orders to process")
            return
        
        logger.info(f"[{datetime.utcnow()}] Found {len(pending_orders)} pending orders to process")
        
        # Process each pending order
        for order in pending_orders:
            # Update status to processing
            order.status = OrderStatus.PROCESSING
            db.commit()
            logger.info(f"  → Order #{order.id} ({order.product_name}) - Status: PROCESSING")
            
            # Simulate processing time (in production, this would be actual business logic)
            # Update status to completed
            order.status = OrderStatus.COMPLETED
            db.commit()
            logger.info(f"  ✓ Order #{order.id} ({order.product_name}) - Status: COMPLETED")
        
        logger.info(f"[{datetime.utcnow()}] Successfully processed {len(pending_orders)} orders")
        
    except Exception as e:
        logger.error(f"[{datetime.utcnow()}] Error processing orders: {str(e)}")
        db.rollback()
    finally:
        # Always close the database session
        db.close()

def start_scheduler():
    """
    Initialize and start the background job scheduler
    - Runs process_pending_orders every 2 minutes
    - Scheduler runs in a separate background thread
    """
    scheduler = BackgroundScheduler()
    
    # Add job to run every 2 minutes (120 seconds)
    # For 3 minutes, change seconds=120 to seconds=180
    scheduler.add_job(
        process_pending_orders,
        'interval',
        seconds=120,  # Run every 2 minutes
        id='process_pending_orders',
        name='Process pending orders',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("✓ Background job scheduler started - Processing orders every 2 minutes")
    
    return scheduler