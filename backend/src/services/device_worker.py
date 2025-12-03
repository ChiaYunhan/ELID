import asyncio
import random
from datetime import datetime
from uuid import UUID
from typing import Dict, Optional
import logging

from ..db.database import SessionLocal
from ..db.models import DeviceType
from .transaction_service import create_transaction
from ..schema.transaction import TransactionCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to track active device workers
active_workers: Dict[UUID, asyncio.Task] = {}

# Sample usernames for random transaction generation
SAMPLE_USERNAMES = [
    "john.doe",
    "jane.smith",
    "bob.jones",
    "alice.williams",
    "charlie.brown",
    "diana.prince",
    "evan.davis",
    "fiona.garcia"
]

# Event types based on device type
EVENT_TYPES = {
    DeviceType.ACCESS_CONTROLLER: [
        "access_granted",
        "access_denied",
        "door_opened",
        "door_closed",
        "access_timeout"
    ],
    DeviceType.FACE_READER: [
        "face_match",
        "face_no_match",
        "face_detected",
        "multiple_faces",
        "face_recognition_error"
    ],
    DeviceType.ANPR: [
        "plate_read",
        "plate_match",
        "plate_no_match",
        "invalid_plate",
        "vehicle_detected"
    ]
}


def generate_transaction_payload(device_type: DeviceType, event_type: str) -> dict:
    """
    Generate metadata/payload based on device type and event.

    Args:
        device_type: Type of device
        event_type: Event type

    Returns:
        Dictionary with relevant metadata
    """
    payload = {
        "confidence": round(random.uniform(0.75, 0.99), 2),
        "processing_time_ms": random.randint(50, 500)
    }

    if device_type == DeviceType.ACCESS_CONTROLLER:
        payload["card_number"] = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        payload["reader_id"] = f"READER-{random.randint(1, 10)}"

    elif device_type == DeviceType.FACE_READER:
        payload["face_id"] = f"FACE-{random.randint(1000, 9999)}"
        payload["image_quality"] = round(random.uniform(0.6, 1.0), 2)

    elif device_type == DeviceType.ANPR:
        plate_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        plate_nums = "0123456789"
        payload["plate_number"] = f"{''.join(random.choices(plate_chars, k=3))}-{''.join(random.choices(plate_nums, k=4))}"
        payload["camera_id"] = f"CAM-{random.randint(1, 5)}"
        payload["vehicle_type"] = random.choice(["car", "truck", "motorcycle", "van"])

    return payload


async def device_worker(device_id: UUID, device_name: str, device_type: DeviceType):
    """
    Background worker that generates transactions for an active device.

    Args:
        device_id: UUID of the device
        device_name: Name of the device
        device_type: Type of device
    """
    logger.info(f"Starting worker for device: {device_name} ({device_id})")

    try:
        while True:
            # Random interval between 2 to 10 seconds
            await asyncio.sleep(random.uniform(2, 10))

            # Generate random transaction
            username = random.choice(SAMPLE_USERNAMES)
            event_type = random.choice(EVENT_TYPES.get(device_type, ["generic_event"]))
            payload = generate_transaction_payload(device_type, event_type)

            # Create transaction in database
            try:
                db = SessionLocal()
                try:
                    transaction_data = TransactionCreate(
                        device_id=device_id,
                        username=username,
                        event_type=event_type,
                        payload=payload
                    )

                    transaction = create_transaction(db, transaction_data)
                    logger.info(
                        f"[{device_name}] Generated transaction: "
                        f"{event_type} for {username} "
                        f"(ID: {transaction.transaction_id})"
                    )
                finally:
                    db.close()

            except Exception as e:
                logger.error(f"Error creating transaction for device {device_id}: {e}")

    except asyncio.CancelledError:
        logger.info(f"Worker for device {device_name} ({device_id}) stopped")
        raise


async def start_device_worker(device_id: UUID, device_name: str, device_type: DeviceType) -> bool:
    """
    Start a background worker for a device.

    Args:
        device_id: UUID of the device
        device_name: Name of the device
        device_type: Type of device

    Returns:
        True if worker started successfully, False if already running
    """
    if device_id in active_workers:
        logger.warning(f"Worker for device {device_id} is already running")
        return False

    # Create and start the worker task
    task = asyncio.create_task(device_worker(device_id, device_name, device_type))
    active_workers[device_id] = task

    logger.info(f"Started worker for device: {device_name} ({device_id})")
    return True


async def stop_device_worker(device_id: UUID) -> bool:
    """
    Stop a background worker for a device.

    Args:
        device_id: UUID of the device

    Returns:
        True if worker stopped successfully, False if not running
    """
    if device_id not in active_workers:
        logger.warning(f"No worker found for device {device_id}")
        return False

    # Cancel the task
    task = active_workers[device_id]
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    # Remove from active workers
    del active_workers[device_id]

    logger.info(f"Stopped worker for device: {device_id}")
    return True


def get_active_worker_count() -> int:
    """
    Get the number of active device workers.

    Returns:
        Number of active workers
    """
    return len(active_workers)


def is_worker_active(device_id: UUID) -> bool:
    """
    Check if a worker is active for a device.

    Args:
        device_id: UUID of the device

    Returns:
        True if worker is active, False otherwise
    """
    return device_id in active_workers


async def stop_all_workers():
    """
    Stop all active device workers.
    Useful for graceful shutdown.
    """
    logger.info(f"Stopping all {len(active_workers)} active workers...")

    device_ids = list(active_workers.keys())
    for device_id in device_ids:
        await stop_device_worker(device_id)

    logger.info("All workers stopped")
