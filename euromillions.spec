# PyInstaller spec file for EuroMillions ML Prediction System
# Run with: pyinstaller euromillions.spec

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define data files to include
datas = [
    ('ui', 'ui'),
    ('requirements.txt', '.'),
    ('.env.example', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# Define hidden imports (modules not automatically detected)
hiddenimports = [
    'streamlit',
    'streamlit.web',
    'streamlit.web.cli',
    'pandas',
    'numpy',
    'lightgbm',
    'sklearn',
    'sklearn.ensemble',
    'sklearn.ensemble._forest',
    'sklearn.tree',
    'sklearn.tree._tree',
    'requests',
    'bs4',
    'lxml',
    'loguru',
    'tenacity',
    'pydantic',
    'python_dotenv',
    'joblib',
    'sqlite3',
    'json',
    'pathlib',
    'datetime',
    'typing',
    'fastapi',
    'uvicorn',
    'typer',
    'orjson',
    'pyarrow',
    'repository',
    'scraper',
    'train_models',
    'streamlit_adapters',
    'config',
    'build_datasets',
]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ (Python ZIP archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE (Executable)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EuroMillions-ML-Prediction',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have one
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following lines for directory distribution:
"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EuroMillions-ML-Prediction'
)
"""
