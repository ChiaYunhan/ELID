from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..db.models import Device, DeviceType, DeviceStatus
from ..schema.device import DeviceCreate, DeviceUpdate


def get_all_devices(db: Session) -> List[Device]:
    """
    Retrieve all devices from the database.

    Args:
        db: Database session

    Returns:
        List of Device objects
    """
    return db.query(Device).all()


def get_device_by_id(db: Session, device_id: UUID) -> Optional[Device]:
    """
    Retrieve a single device by ID.

    Args:
        db: Database session
        device_id: UUID of the device

    Returns:
        Device object if found, None otherwise
    """
    return db.query(Device).filter(Device.id == device_id).first()


def get_active_devices(db: Session) -> List[Device]:
    """
    Retrieve all devices with ACTIVE status.

    Args:
        db: Database session

    Returns:
        List of Device objects with ACTIVE status
    """
    return db.query(Device).filter(Device.status == DeviceStatus.ACTIVE).all()


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    """
    Create a new device in the database.

    Args:
        db: Database session
        device_data: Device creation data

    Returns:
        Created Device object

    Raises:
        ValueError: If device_type is invalid
        IntegrityError: If database constraint is violated
    """
    # Validate device_type
    try:
        device_type_enum = DeviceType[device_data.device_type.upper()]
    except KeyError:
        valid_types = [dt.value for dt in DeviceType]
        raise ValueError(f"Invalid device_type. Must be one of: {valid_types}")

    # Create device with INACTIVE status by default
    db_device = Device(
        name=device_data.name,
        device_type=device_type_enum,
        ip_address=device_data.ip_address,
        status=DeviceStatus.INACTIVE,
    )

    try:
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device
    except IntegrityError as e:
        db.rollback()
        raise e


def toggle_device_status(db: Session, device_id: UUID) -> Optional[Device]:
    """
    Toggle device status between ACTIVE and INACTIVE.
    If device is ACTIVE, set to INACTIVE and vice versa.

    Args:
        db: Database session
        device_id: UUID of the device

    Returns:
        Updated Device object if found, None otherwise
    """
    db_device = get_device_by_id(db, device_id)

    if not db_device:
        return None

    # Toggle status
    db_device.status = (
        DeviceStatus.INACTIVE
        if db_device.status == DeviceStatus.ACTIVE
        else DeviceStatus.ACTIVE
    )

    try:
        db.commit()
        db.refresh(db_device)
        return db_device
    except IntegrityError as e:
        db.rollback()
        raise e
