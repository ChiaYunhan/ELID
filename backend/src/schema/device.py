from pydantic import BaseModel, IPvAnyAddress
from datetime import datetime
from uuid import UUID
from typing import Optional


class DeviceBase(BaseModel):
    """Base schema for Device"""
    name: str
    device_type: str  # "access_controller", "face_reader", "anpr"
    ip_address: str


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    pass


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""
    name: Optional[str] = None
    device_type: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[str] = None


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
