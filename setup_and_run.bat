@echo off
echo ========================================
echo  EuroMillions ML - Setup & First Run
echo ========================================
echo.
echo This will:
echo - Create virtual environment
echo - Install dependencies
echo - Launch the application
echo.
pause

cd /d "%~dp0"

REM Run bootstrap script
echo Running setup...
powershell -ExecutionPolicy Bypass -File bootstrap.ps1

echo.
echo Setup completed! The application should now be running.
echo Check your browser at: http://localhost:8501
echo.
pause