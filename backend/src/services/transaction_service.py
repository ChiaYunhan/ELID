from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..db.models import Transaction, Device
from ..schema.transaction import TransactionCreate


def get_all_transactions(
    db: Session, limit: Optional[int] = None, offset: int = 0
) -> List[Transaction]:
    """
    Retrieve all transactions from the database.

    Args:
        db: Database session
        limit: Maximum number of transactions to return (optional)
        offset: Number of transactions to skip (default: 0)

    Returns:
        List of Transaction objects, ordered by timestamp (newest first)
    """
    query = db.query(Transaction).order_by(Transaction.timestamp.desc())

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query.all()


def create_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    """
    Create a new transaction in the database.

    Args:
        db: Database session
        transaction_data: Transaction creation data

    Returns:
        Created Transaction object

    Raises:
        ValueError: If device does not exist
        IntegrityError: If database constraint is violated
    """
    # Verify device exists
    device = db.query(Device).filter(Device.id == transaction_data.device_id).first()
    if not device:
        raise ValueError(f"Device with id {transaction_data.device_id} does not exist")

    # Create transaction
    db_transaction = Transaction(
        device_id=transaction_data.device_id,
        username=transaction_data.username,
        event_type=transaction_data.event_type,
        payload=transaction_data.payload,
        timestamp=datetime.utcnow()
    )

    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except IntegrityError as e:
        db.rollback()
        raise e
