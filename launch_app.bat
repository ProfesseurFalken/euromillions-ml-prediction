@echo off
echo ========================================
echo  EuroMillions ML Prediction System
echo ========================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first to initialize the environment.
    pause
    exit /b 1
)

REM Activate virtual environment and launch
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Launching Streamlit application...
echo.
echo The application will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

python main.py

echo.
echo Application stopped.
pause