@echo off
echo ==========================================
echo   Internship Portal - Startup Script
echo ==========================================

:: Check if .venv exists, if not create it
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

:: Install/Update requirements using uv if available, else pip
echo Installing dependencies...
where uv >nul 2>&1
if %errorlevel%==0 (
    echo Using uv for fast installation...
    uv pip install -r requirements.txt
) else (
    pip install -r requirements.txt
)

:: Start Flask application
echo Starting Flask application...
python app.py

pause
