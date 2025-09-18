@echo off
echo ========================================
echo FARAMEX AI - PostgreSQL Setup
echo ========================================

echo.
echo 1. Installing PostgreSQL dependencies...
pip install -r requirements_postgres.txt

echo.
echo 2. Setting up environment variables...
echo Please make sure your .env file contains:
echo.
echo DATABASE_URL=postgresql://username:password@localhost:5432/faramex_db
echo DB_HOST=localhost
echo DB_PORT=5432
echo DB_NAME=faramex_db
echo DB_USER=your_username
echo DB_PASSWORD=your_password
echo.

echo 3. PostgreSQL Installation Instructions:
echo.
echo Windows:
echo - Download PostgreSQL from: https://www.postgresql.org/download/windows/
echo - Install with default settings
echo - Remember the password you set for 'postgres' user
echo - Default port is 5432
echo.
echo After installation:
echo - Open pgAdmin or psql
echo - Create database: CREATE DATABASE faramex_db;
echo - Create user: CREATE USER your_username WITH PASSWORD 'your_password';
echo - Grant privileges: GRANT ALL PRIVILEGES ON DATABASE faramex_db TO your_username;
echo.

echo 4. Update your .env file with actual database credentials
echo.
echo 5. Run the server: python main_simple.py
echo.

pause
