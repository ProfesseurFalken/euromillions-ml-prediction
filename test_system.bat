@echo off
echo ========================================
echo  EuroMillions ML - Quick Test
echo ========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Please run setup_and_run.bat first!
    pause
    exit /b 1
)

echo Running comprehensive system test...
echo.

call .venv\Scripts\activate.bat
python comprehensive_test.py

echo.
echo Test completed!
pause