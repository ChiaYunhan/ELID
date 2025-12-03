import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .database import Base


class DeviceType(str, enum.Enum):
    """Enum for device types"""
    ACCESS_CONTROLLER = "access_controller"
    FACE_READER = "face_reader"
    ANPR = "anpr"


class DeviceStatus(str, enum.Enum):
    """Enum for device status"""
    INACTIVE = "inactive"
    ACTIVE = "active"


class Device(Base):
    """Device model representing physical/logical devices"""
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    ip_address = Column(String, nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.INACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, type={self.device_type}, status={self.status})>"


class Transaction(Base):
    """Transaction model representing device events/transactions"""
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    username = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to device
    device = relationship("Device", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, device_id={self.device_id}, event={self.event_type}, user={self.username})>"
