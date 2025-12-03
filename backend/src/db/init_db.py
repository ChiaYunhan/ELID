"""
Database initialization script.
Run this script to create all tables in the PostgreSQL database.
"""

from .database import init_db, engine
from .models import Device, Transaction


def main():
    """Initialize the database by creating all tables"""
    print("Starting database initialization...")
    print(f"Connecting to database: {engine.url}")

    try:
        init_db()
        print("\n[SUCCESS] Database tables created successfully!")
        print("\nCreated tables:")
        print("  - devices")
        print("  - transactions")
    except Exception as e:
        print(f"\n[ERROR] Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    main()
