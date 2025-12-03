from typing import List, Optional
from uuid import UUID
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import logging

from .db.database import get_db, SessionLocal, init_db
from .schema.device import DeviceCreate, DeviceUpdate, DeviceResponse
from .schema.transaction import TransactionCreate, TransactionResponse
from .services import device_service, transaction_service
from .services.device_worker import (
    start_device_worker,
    stop_device_worker,
    stop_all_workers,
    get_active_worker_count,
    is_worker_active,
)
from .db.models import DeviceStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database and start workers for all active devices
    logger.info("Application startup: Initializing database...")

    # Initialize database tables
    try:
        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

    db = SessionLocal()
    try:
        logger.info("Starting device workers...")

        # Get all active devices from database
        active_devices = device_service.get_active_devices(db)

        if active_devices:
            logger.info(
                f"Found {len(active_devices)} active device(s). Starting workers..."
            )

            for device in active_devices:
                await start_device_worker(device.id, device.name, device.device_type)
                logger.info(f"Restored worker for device: {device.name} ({device.id})")

            logger.info(f"Successfully started {len(active_devices)} device worker(s)")
        else:
            logger.info("No active devices found. No workers to start.")
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
    finally:
        db.close()

    # Yield control to the application
    yield

    # Shutdown: Stop all device workers
    logger.info("Application shutdown: Stopping all device workers...")
    try:
        await stop_all_workers()
        logger.info("All device workers stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title="ELID Device Management API",
    description="API for managing devices and their transactions",
    version="1.0.0",
    lifespan=lifespan,  # Register lifespan context manager
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def root():
    """Root endpoint - health check"""
    return {"status": "ok", "message": "ELID API is running"}


# ==================== Device Endpoints ====================


@app.get("/devices/list", response_model=List[DeviceResponse])
def get_all_devices(db: Session = Depends(get_db)):
    """
    Retrieve all devices from the database.

    Returns:
        List of all devices with their current status
    """
    try:
        devices = device_service.get_all_devices(db)
        return devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving devices: {str(e)}",
        )


@app.post(
    "/devices/create",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device in the database.

    Args:
        device_data: Device information (name, device_type, ip_address)

    Returns:
        Created device with INACTIVE status
    """
    try:
        device = device_service.create_device(db, device_data)
        return device
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating device: {str(e)}",
        )


@app.put("/devices/{device_id}", response_model=DeviceResponse)
async def toggle_device_status(device_id: UUID, db: Session = Depends(get_db)):
    """
    Toggle device status between ACTIVE and INACTIVE.
    If device is currently ACTIVE, it will be set to INACTIVE and vice versa.

    When activating a device, a background worker is started to generate transactions.
    When deactivating, the worker is stopped.

    Args:
        device_id: UUID of the device

    Returns:
        Updated device information with new status
    """
    try:
        device = device_service.toggle_device_status(db, device_id)

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found",
            )

        # Manage worker based on new status
        if device.status == DeviceStatus.ACTIVE:
            # Start worker for the device
            await start_device_worker(device.id, device.name, device.device_type)
        else:
            # Stop worker for the device
            await stop_device_worker(device.id)

        return device
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling device status: {str(e)}",
        )


@app.get("/devices/workers/status")
def get_workers_status():
    """
    Get status of active device workers.

    Returns:
        Information about active workers
    """
    return {
        "active_worker_count": get_active_worker_count(),
        "message": f"{get_active_worker_count()} device(s) currently generating transactions",
    }


# ==================== Transaction Endpoints ====================


@app.get("/transactions/list", response_model=List[TransactionResponse])
def get_all_transactions(
    limit: Optional[int] = 100, offset: int = 0, db: Session = Depends(get_db)
):
    """
    Retrieve all transactions from the database.

    Args:
        limit: Maximum number of transactions to return (default: 100)
        offset: Number of transactions to skip (default: 0)

    Returns:
        List of transactions ordered by timestamp (newest first)
    """
    try:
        transactions = transaction_service.get_all_transactions(
            db, limit=limit, offset=offset
        )
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transactions: {str(e)}",
        )
