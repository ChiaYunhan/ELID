# ELID - Event Logging and Intelligent Device Management

A full-stack application for managing IoT devices and tracking their transaction events in real-time.

## Quick Start

### Prerequisites
- Docker
- Node.js 18+
- Python 3.8+

### 1. Start PostgreSQL Database (Docker)

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=mydatabase \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:latest
```

### 2. Backend Setup

```bash
cd ELID/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start the backend server
cd src
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Credentials

### Database (PostgreSQL Docker Container)
- **Database Name:** `mydatabase`
- **Username:** `myuser`
- **Password:** `mypassword`
- **Host:** `localhost`
- **Port:** `5432`
- **Connection String:** `postgresql://myuser:mypassword@localhost:5432/mydatabase`

### API Access
- No authentication required
- API Base URL: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

## Architecture Design

**ELID** is a FastAPI-based backend with a React TypeScript frontend that manages IoT devices and their transaction events. The architecture emphasizes real-time event processing with asynchronous background workers.

**Key Design Decisions:**
1. **Device Worker Pattern** - Each active device gets its own asyncio background task that generates simulated transactions at random intervals (2-10 seconds), enabling concurrent multi-device simulation without blocking the main event loop.

2. **Lifespan Management** - The FastAPI lifespan context manager automatically restores workers for all active devices on startup by querying the database, ensuring stateful device operations survive server restarts.

3. **Layered Service Architecture** - Business logic is separated into service modules (`device_service`, `transaction_service`, `device_worker`) while maintaining SQLAlchemy ORM for database operations, allowing clean separation between API routes, business logic, and data access.

4. **Type-Safe Device Models** - Python Enums define device types (Access Controller, Face Reader, ANPR) and statuses (Active/Inactive), with Pydantic schemas ensuring type safety across API boundaries and generating appropriate mock event payloads per device type.

5. **PostgreSQL with JSON Payloads** - Transactions use PostgreSQL's JSON column type for flexible metadata storage, allowing different device types to store varied event data without schema changes while maintaining relational integrity through foreign keys.
