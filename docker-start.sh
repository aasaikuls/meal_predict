#!/bin/bash

echo "========================================"
echo "Building and Starting Docker Containers"
echo "========================================"
echo ""

# Read LOG_DRIVER from .env (strip inline comments and whitespace)
LOG_DRIVER=$(grep -E '^LOG_DRIVER=' .env 2>/dev/null | head -1 | cut -d'=' -f2 | sed 's/[[:space:]]*#.*//' | tr -d '[:space:]')
LOG_DRIVER=${LOG_DRIVER:-json}

if [ "$LOG_DRIVER" = "awslogs" ]; then
    echo "Log driver: awslogs (CloudWatch)"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.logging-awslogs.yml"
else
    echo "Log driver: json-file (local)"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.logging-json.yml"
fi

docker-compose $COMPOSE_FILES up --build

echo ""
echo "========================================"
echo "Containers stopped"
echo "========================================"
echo ""
echo "To start in background: docker-compose $COMPOSE_FILES up -d"
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "========================================"
