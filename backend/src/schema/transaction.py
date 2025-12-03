from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class TransactionBase(BaseModel):
    """Base schema for Transaction"""
    username: str
    event_type: str
    payload: Optional[Dict[str, Any]] = None


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    device_id: UUID


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    transaction_id: UUID
    device_id: UUID
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
