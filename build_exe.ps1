# Build script for EuroMillions ML Prediction System
# Creates a standalone executable using PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " EuroMillions ML - Build Executable" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "[ERROR] Virtual environment not found. Run bootstrap.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install PyInstaller if not present
Write-Host "[INFO] Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller

# Clean previous builds
Write-Host "[INFO] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the executable
Write-Host "[INFO] Building executable..." -ForegroundColor Yellow
pyinstaller euromillions.spec

# Check if build was successful
if (Test-Path "dist\EuroMillions-ML-Prediction.exe") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    $exeFile = Get-Item "dist\EuroMillions-ML-Prediction.exe"
    $sizeGB = [math]::Round($exeFile.Length / 1GB, 2)
    $sizeMB = [math]::Round($exeFile.Length / 1MB, 2)
    
    Write-Host "Executable created: dist\EuroMillions-ML-Prediction.exe" -ForegroundColor Green
    Write-Host "Size: $sizeMB MB ($sizeGB GB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now distribute this single file!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] To test the executable:" -ForegroundColor Yellow
    Write-Host "  cd dist" -ForegroundColor Yellow
    Write-Host "  .\EuroMillions-ML-Prediction.exe" -ForegroundColor Yellow
    Write-Host ""
    
    # Optionally open the dist folder
    $choice = Read-Host "Open dist folder? (y/n)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        Invoke-Item "dist"
    }
    
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host " BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for errors." -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
