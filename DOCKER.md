# Docker Setup for ELID Device Management System

This guide explains how to run the ELID application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Services

The application consists of three services:

1. **PostgreSQL Database** - Stores devices and transactions
2. **Backend API** - FastAPI application on port 8000
3. **Frontend** - React + Vite application on port 5173

## Quick Start

### 1. Start all services

From the ELID directory, run:

```bash
docker-compose up -d
```

This will:
- Build the backend and frontend Docker images
- Start PostgreSQL database
- Start the backend API server
- Start the frontend development server

### 2. Check service status

```bash
docker-compose ps
```

You should see three running containers:
- `elid-postgres` on port 5432
- `elid-backend` on port 8000
- `elid-frontend` on port 5173

### 3. Access the application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. View logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for a specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## Database Initialization

The database will be automatically initialized when the backend starts. The backend service waits for PostgreSQL to be healthy before starting.

## Stopping the Application

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (this will delete all data):
```bash
docker-compose down -v
```

## Development Workflow

The Docker setup is configured for development with hot-reloading:

### Backend Changes
- Changes to Python files will automatically reload the FastAPI server
- Backend code is mounted as a volume at `/app`

### Frontend Changes
- Changes to React/TypeScript files will automatically refresh the browser
- Frontend code is mounted as a volume at `/app`
- `node_modules` is preserved in a separate volume

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string (configured in docker-compose.yml)
- `PYTHONUNBUFFERED`: Ensures Python output is sent directly to logs

### Frontend
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Troubleshooting

### Database connection errors

If the backend can't connect to the database:

1. Check if PostgreSQL is healthy:
   ```bash
   docker-compose ps postgres
   ```

2. Restart the backend:
   ```bash
   docker-compose restart backend
   ```

### Port conflicts

If ports 5432, 8000, or 5173 are already in use, edit `docker-compose.yml` to change the port mappings:

```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

### Rebuilding containers

If you've made changes to Dockerfile or dependencies:

```bash
docker-compose up -d --build
```

### Clearing everything

To start fresh:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

For production, you should:

1. Update CORS settings in [backend/src/main.py](backend/src/main.py) to include your production domain
2. Use proper environment variables for database credentials
3. Build the frontend for production (replace dev server with nginx or similar)
4. Use secrets management for sensitive data
5. Configure proper logging and monitoring

## Database Access

To access the PostgreSQL database directly:

```bash
docker-compose exec postgres psql -U elid_user -d elid_db
```

Common commands:
- `\dt` - List tables
- `\d devices` - Describe devices table
- `SELECT * FROM devices;` - Query devices
- `\q` - Exit

## Backup and Restore

### Backup database

```bash
docker-compose exec postgres pg_dump -U elid_user elid_db > backup.sql
```

### Restore database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U elid_user elid_db
```
