@echo off
REM GUI Build tool for EuroMillions ML Prediction System
REM Uses Auto-Py-To-Exe for graphical interface

echo ========================================
echo  EuroMillions ML - GUI Build Tool
echo ========================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found. Run bootstrap.ps1 first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install Auto-Py-To-Exe
echo [INFO] Installing Auto-Py-To-Exe...
pip install auto-py-to-exe

REM Launch the GUI
echo [INFO] Launching Auto-Py-To-Exe GUI...
echo.
echo Instructions:
echo 1. Set Script Location to: main.py
echo 2. Select "One File" output
echo 3. Select "Console Based" (or Window Based for no console)
echo 4. Add Additional Files: ui folder, requirements.txt, .env.example
echo 5. Add Hidden Imports (see build notes)
echo 6. Click "Convert .py to .exe"
echo.

auto-py-to-exe

pause
