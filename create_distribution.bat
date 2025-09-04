@echo off
REM Package EuroMillions ML for distribution

echo ========================================
echo  EuroMillions ML - Create Distribution
echo ========================================

if not exist "dist\EuroMillions-ML-Prediction.exe" (
    echo [ERROR] Executable not found! Run build_exe.bat first.
    pause
    exit /b 1
)

REM Create distribution folder
set DIST_NAME=EuroMillions-ML-v1.0
if exist "%DIST_NAME%" rmdir /s /q "%DIST_NAME%"
mkdir "%DIST_NAME%"

echo [INFO] Creating distribution package...

REM Copy executable
copy "dist\EuroMillions-ML-Prediction.exe" "%DIST_NAME%\"

REM Copy documentation
copy "README.md" "%DIST_NAME%\README.txt"
copy "LICENSE" "%DIST_NAME%\LICENSE.txt"
copy "BUILD_EXECUTABLE.md" "%DIST_NAME%\BUILD_GUIDE.txt"

REM Create user guide
echo EuroMillions ML Prediction System - Guide Utilisateur > "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo ===================================================== >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo. >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo LANCEMENT : >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 1. Double-cliquer sur EuroMillions-ML-Prediction.exe >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 2. Attendre le chargement (peut prendre 30 secondes) >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 3. Le navigateur s'ouvrira automatiquement >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 4. URL: http://localhost:8501 >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo. >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo PREMIERE UTILISATION : >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 1. Aller dans 'Gestion des Donnees' >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 2. Cliquer 'Initialiser l'historique complet' >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 3. Aller dans 'Entrainement des Modeles' >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 4. Cliquer 'Entrainer a partir de zero' >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo 5. Aller dans 'Generation de Tickets' pour les predictions >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo. >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo IMPORTANT: >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo - Connexion Internet requise pour les donnees >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"
echo - Systeme educatif uniquement, pas de garantie de gains >> "%DIST_NAME%\GUIDE_UTILISATEUR.txt"

REM Create checksums
certutil -hashfile "%DIST_NAME%\EuroMillions-ML-Prediction.exe" MD5 > "%DIST_NAME%\checksums.txt"
certutil -hashfile "%DIST_NAME%\EuroMillions-ML-Prediction.exe" SHA256 >> "%DIST_NAME%\checksums.txt"

echo [INFO] Package created: %DIST_NAME%\

REM Show contents
echo [INFO] Package contents:
dir "%DIST_NAME%" /b

REM Create ZIP if 7-Zip or WinRAR available
where 7z >nul 2>nul
if %errorlevel%==0 (
    echo [INFO] Creating ZIP archive with 7-Zip...
    7z a "%DIST_NAME%.zip" "%DIST_NAME%\*"
    echo [INFO] ZIP created: %DIST_NAME%.zip
) else (
    echo [INFO] 7-Zip not found. Manual compression recommended.
)

echo.
echo ========================================
echo  DISTRIBUTION READY!
echo ========================================
echo.
echo Package folder: %DIST_NAME%\
echo Executable size: 
dir "%DIST_NAME%\EuroMillions-ML-Prediction.exe" | find "EuroMillions-ML-Prediction.exe"
echo.

pause
