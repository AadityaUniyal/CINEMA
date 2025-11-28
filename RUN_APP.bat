@echo off
echo ==========================================
echo Starting MovieLens Application
echo ==========================================
echo.

REM Check if MongoDB is running
echo Checking MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting MongoDB...
    net start MongoDB
    timeout /t 3 >nul
)
echo MongoDB is running
echo.

REM Start Backend
echo Starting Backend Server...
start "MovieLens Backend" cmd /k "cd backend && python app.py"
timeout /t 5 >nul

REM Start Frontend
echo Starting Frontend...
start "MovieLens Frontend" cmd /k "cd frontend && npm start"

echo.
echo ==========================================
echo Application is starting!
echo ==========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all services...
pause >nul

REM Stop services
taskkill /FI "WindowTitle eq MovieLens Backend*" /T /F
taskkill /FI "WindowTitle eq MovieLens Frontend*" /T /F
echo.
echo Services stopped.
pause
