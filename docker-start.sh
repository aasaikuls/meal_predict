#!/bin/bash

echo "========================================"
echo "Building and Starting Docker Containers"
echo "========================================"
echo ""

docker compose up --build

echo ""
echo "========================================"
echo "Containers stopped"
echo "========================================"
echo ""
echo "To start in background: docker compose up -d"
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
echo ""
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "========================================"
