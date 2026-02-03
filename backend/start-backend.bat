@echo off
echo ========================================
echo Setting up Backend Virtual Environment
echo ========================================

cd backend

REM Check if venv exists, if not create it
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting Backend Server (FastAPI)
echo ========================================
python main.py
