@echo off
echo ========================================
echo    Proma AI - Setup and Run Script
echo ========================================

echo.
echo [1/3] Installing Python dependencies...
pip install -r requirements_postgres.txt

echo.
echo [2/3] Setting up environment...
if not exist .env (
    echo Creating .env file...
    copy .env.example .env 2>nul || echo Please create .env file manually
)

echo.
echo [3/3] Starting Proma AI Server...
echo Server will be available at: http://localhost:8000
echo Dashboard: http://localhost:8000/frontend/dashboard.html
echo.

python main_simple.py

pause
