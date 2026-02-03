#!/bin/bash

echo "========================================"
echo "Starting Backend Server (FastAPI in venv)"
echo "========================================"
cd backend
chmod +x start-backend.sh
./start-backend.sh &
BACKEND_PID=$!
sleep 5

echo ""
echo "========================================"
echo "Starting Frontend Server (React)"
echo "========================================"
cd ../frontend
PORT=3001 npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Servers are running..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
