# 🚀 Création d'un Exécutable EuroMillions

Ce guide explique comment créer un fichier exécutable standalone (.exe) pour le système EuroMillions ML.

## 📋 Prérequis

- Python 3.9+ installé
- Projet EuroMillions configuré (avoir exécuté `bootstrap.ps1`)
- Environnement virtuel fonctionnel

## 🛠️ Méthodes de Création

### **Méthode 1 : Script Automatique (Recommandée)**

```bash
# Windows PowerShell
.\build_exe.ps1

# Ou via CMD
build_exe.bat
```

### **Méthode 2 : Interface Graphique**

```bash
# Lance Auto-Py-To-Exe avec interface graphique
build_gui.bat
```

### **Méthode 3 : Manuelle avec PyInstaller**

```bash
# 1. Activer l'environnement virtuel
.\.venv\Scripts\activate

# 2. Installer PyInstaller
pip install pyinstaller

# 3. Créer l'exécutable
pyinstaller euromillions.spec

# 4. L'exécutable sera dans le dossier dist/
```

## 📁 Structure de Sortie

Après compilation, vous obtiendrez :

```
dist/
└── EuroMillions-ML-Prediction.exe  (≈ 500-800 MB)
```

## 🎯 Configuration de Build

### **Fichiers Inclus Automatiquement**
- ✅ Interface Streamlit (dossier `ui/`)
- ✅ Tous les modules Python requis
- ✅ Dépendances ML (LightGBM, scikit-learn, pandas)
- ✅ Configuration exemple (`.env.example`)
- ✅ Documentation (`README.md`, `LICENSE`)

### **Modules Cachés Détectés**
```python
hiddenimports = [
    'streamlit', 'pandas', 'numpy', 'lightgbm', 'sklearn',
    'requests', 'bs4', 'lxml', 'loguru', 'tenacity',
    'pydantic', 'python_dotenv', 'joblib', 'sqlite3'
]
```

## 🚀 Utilisation de l'Exécutable

### **Première Utilisation**
1. Copier `EuroMillions-ML-Prediction.exe` sur le système cible
2. Double-cliquer pour lancer
3. L'application créera automatiquement :
   - Dossier `data/` pour la base de données
   - Dossier `models/` pour les modèles ML
   - Fichier `.env` de configuration
4. Navigateur s'ouvrira automatiquement sur `http://localhost:8501`

### **Fonctionnalités Disponibles**
- ✅ Interface Streamlit complète
- ✅ Scraping des données UK National Lottery
- ✅ Entraînement des modèles ML
- ✅ Génération de prédictions
- ✅ Export des données
- ✅ Configuration via interface

## ⚙️ Options de Build

### **Exécutable Unique (Par Défaut)**
- Un seul fichier `.exe`
- Plus lent au démarrage
- Plus facile à distribuer

### **Distribution en Dossier**
```bash
# Modifier euromillions.spec : décommenter la section COLLECT
pyinstaller euromillions.spec
```
- Dossier avec .exe + DLLs
- Démarrage plus rapide
- Plus volumineux à distribuer

### **Version Sans Console**
```python
# Dans euromillions.spec, changer :
console=False  # au lieu de True
```

## 🐛 Résolution de Problèmes

### **Erreur "Module not found"**
```bash
# Ajouter le module manquant dans hiddenimports de euromillions.spec
hiddenimports = ['module_manquant']
```

### **Erreur "Failed to execute script"**
```bash
# Compiler avec debug activé
console=True  # dans euromillions.spec
debug=True    # dans euromillions.spec
```

### **Taille de l'Exécutable Trop Grande**
```bash
# Exclure des modules non utilisés dans euromillions.spec
excludes=[
    'matplotlib', 'tkinter', 'PyQt5', 'PyQt6'
]
```

### **Lenteur au Démarrage**
- Utiliser la distribution en dossier plutôt qu'un fichier unique
- Exclure les modules non essentiels

## 📊 Performances

| Type | Taille | Temps Démarrage | Distribution |
|------|--------|-----------------|--------------|
| Un fichier | ~600 MB | ~15-30s | ⭐⭐⭐ |
| Dossier | ~800 MB | ~5-10s | ⭐⭐ |

## 🔒 Sécurité

### **Antivirus**
- L'exécutable peut être détecté comme suspect (faux positif)
- Soumettre à VirusTotal pour vérification
- Signer le code si distribution publique

### **Distribution**
- Compresser avec 7-Zip ou WinRAR
- Inclure un README avec instructions
- Fournir checksums MD5/SHA256

## 📦 Distribution Recommandée

```
EuroMillions-ML-v1.0/
├── EuroMillions-ML-Prediction.exe
├── README-Executable.txt
├── LICENCE.txt
└── checksums.txt
```

## 🎉 Exemple de Distribution

```bash
# Créer un package de distribution
New-Item -ItemType Directory -Name "EuroMillions-ML-v1.0"
Copy-Item "dist\EuroMillions-ML-Prediction.exe" "EuroMillions-ML-v1.0\"
Copy-Item "README.md" "EuroMillions-ML-v1.0\README-Executable.txt"
Copy-Item "LICENSE" "EuroMillions-ML-v1.0\"

# Compresser
Compress-Archive -Path "EuroMillions-ML-v1.0" -DestinationPath "EuroMillions-ML-v1.0.zip"
```

L'exécutable est maintenant prêt pour distribution ! 🎯
