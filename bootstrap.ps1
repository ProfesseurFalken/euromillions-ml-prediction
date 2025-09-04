Param([string]$Py="python",[string]$Req="requirements.txt")
Write-Host ">>> Checking Python..."
$ver = & $Py -V 2>$null; if ($LASTEXITCODE -ne 0) { Write-Error "Python not found (install 3.11)."; exit 1 }
Write-Host ">>> Creating venv..."; & $Py -m venv .venv
Write-Host ">>> Activating + upgrading pip..."; . .\.venv\Scripts\Activate.ps1; & $Py -m pip install --upgrade pip
Write-Host ">>> Installing requirements..."; if (-Not (Test-Path $Req)) { Write-Error "requirements.txt missing"; exit 1 }; pip install -r $Req
Write-Host ">>> Ensuring .env and folders..."; if (-Not (Test-Path ".env") -and (Test-Path ".env.example")) { Copy-Item ".env.example" ".env" }
New-Item -ItemType Directory -Force -Path "data","data\raw","data\processed","models\euromillions" | Out-Null
Write-Host ">>> Bootstrap done. Launching UI..."; streamlit run ui\streamlit_app.py
