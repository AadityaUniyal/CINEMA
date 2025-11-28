@echo off
echo ==========================================
echo MovieLens Setup Script
echo ==========================================
echo.

REM Backend setup
echo Setting up backend...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies
    exit /b 1
)
echo Backend dependencies installed
echo.

REM Initialize database
echo Initializing database with CSV data...
python init_db.py
if %errorlevel% neq 0 (
    echo Database initialization failed
    exit /b 1
)
echo.

REM Frontend setup
echo Setting up frontend...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies
    exit /b 1
)
echo Frontend dependencies installed
echo.

cd ..
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To start the application:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   python app.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm start
echo.
echo Or use Docker:
echo   docker-compose up
echo.
pause
