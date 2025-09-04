@echo off
REM Build script for EuroMillions ML Prediction System
REM Creates a standalone executable using PyInstaller

echo ========================================
echo  EuroMillions ML - Build Executable
echo ========================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found. Run bootstrap.ps1 first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install PyInstaller if not present
echo [INFO] Installing PyInstaller...
pip install pyinstaller

REM Clean previous builds
echo [INFO] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build the executable
echo [INFO] Building executable...
pyinstaller euromillions.spec

REM Check if build was successful
if exist "dist\EuroMillions-ML-Prediction.exe" (
    echo.
    echo ========================================
    echo  BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\EuroMillions-ML-Prediction.exe
    echo Size: 
    dir "dist\EuroMillions-ML-Prediction.exe" | find "EuroMillions-ML-Prediction.exe"
    echo.
    echo You can now distribute this single file!
    echo.
    echo [INFO] To test the executable:
    echo   cd dist
    echo   EuroMillions-ML-Prediction.exe
    echo.
) else (
    echo.
    echo ========================================
    echo  BUILD FAILED!
    echo ========================================
    echo.
    echo Check the output above for errors.
    echo.
)

pause
