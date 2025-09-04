@echo off
REM Test script for EuroMillions ML Prediction executable

echo ========================================
echo  Testing EuroMillions ML Executable
echo ========================================

if not exist "dist\EuroMillions-ML-Prediction.exe" (
    echo [ERROR] Executable not found! Run build_exe.bat first.
    pause
    exit /b 1
)

echo [INFO] Executable found: EuroMillions-ML-Prediction.exe
echo [INFO] Size: 
dir "dist\EuroMillions-ML-Prediction.exe" | find "EuroMillions-ML-Prediction.exe"

echo.
echo [INFO] Testing executable launch...
echo [WARN] This will start the application in a new window.
echo [WARN] Close the application manually after testing.
echo.

set /p choice="Launch test? (y/n): "
if /i "%choice%"=="y" (
    echo [INFO] Starting executable...
    cd dist
    start EuroMillions-ML-Prediction.exe
    echo [INFO] Application started. Check for browser opening at http://localhost:8501
) else (
    echo [INFO] Test cancelled.
)

pause
