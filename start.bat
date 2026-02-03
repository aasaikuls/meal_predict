@echo off
echo ========================================
echo Starting Backend Server (FastAPI in venv)
echo ========================================
cd backend
start cmd /k "call start-backend.bat"
timeout /t 5

echo.
echo ========================================
echo Starting Frontend Server (React)
echo ========================================
cd ..\frontend
start cmd /k "npm start"

echo.
echo ========================================
echo Servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul
