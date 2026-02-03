# Docker Deployment Guide

This application is fully containerized and can be quickly deployed on any VM with Docker installed.

## Prerequisites

- Docker Engine (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)

## Quick Start

### Windows
```cmd
docker-start.bat
```

### Linux/Mac
```bash
chmod +x docker-start.sh
./docker-start.sh
```

## Manual Commands

### Build and Start Containers
```bash
docker-compose up --build
```

### Start in Background (Detached Mode)
```bash
docker-compose up -d
```

### Stop Containers
```bash
docker-compose down
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Frontend logs only
docker-compose logs -f frontend
```

### Rebuild Containers
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Access the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## Container Structure

### Backend Container
- **Image**: Python 3.11 slim
- **Port**: 8001
- **Files**: 
  - main.py (FastAPI application)
  - ai_summary.py (AI summary endpoints)
  - meal_planning.py (Meal planning logic)
- **Volumes**: CSV data files and PredictionResults mounted from host

### Frontend Container
- **Image**: Node 18 Alpine
- **Port**: 3001
- **Files**: React application with all dependencies

## Data Files

The following CSV files are mounted as volumes from the host machine:
- Age.csv
- Destination.csv
- MealTime.csv
- Nationality.csv
- PredictionResults/ (directory)

These files are automatically available to the backend container at runtime.

## Deployment to New VM

1. Copy the entire project directory to the VM
2. Install Docker and Docker Compose
3. Run the startup script:
   ```bash
   ./docker-start.sh
   ```

That's it! The application will be up and running.

## Troubleshooting

### Port Already in Use
If ports 8001 or 3001 are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8002:8001"  # Change host port (left side)
```

### Container Won't Start
Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Reset Everything
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Environment Variables

Frontend environment variables can be configured in `docker-compose.yml`:
```yaml
environment:
  - REACT_APP_API_URL=http://localhost:8001
  - PORT=3001
```

Backend environment variables can be added as needed:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - YOUR_ENV_VAR=value
```
