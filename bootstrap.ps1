Param(
    [string]$Py = "python",
    [string]$Req = "requirements.txt"
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Message,
        [scriptblock]$Action
    )

    Write-Host ">>> $Message"
    & $Action
}

try {
    Invoke-Step "Checking Python..." {
        & $Py -V > $null
    }

    $venvRoot = Join-Path (Get-Location).Path ".venv"
    $venvPython = Join-Path $venvRoot "Scripts\python.exe"

    if (-not (Test-Path $venvPython)) {
        Invoke-Step "Creating virtual environment..." {
            & $Py -m venv ".venv"
        }
    }
    else {
        Write-Host ">>> Using existing virtual environment"
    }

    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment not found at $venvPython"
    }

    Invoke-Step "Upgrading pip..." {
        & $venvPython -m pip install --upgrade pip
    }

    Invoke-Step "Installing requirements..." {
        if (-not (Test-Path $Req)) {
            throw "Requirements file not found: $Req"
        }
        & $venvPython -m pip install -r $Req
    }

    Invoke-Step "Ensuring .env and folders..." {
        if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
            Copy-Item ".env.example" ".env"
        }

        $paths = @(
            "data",
            "data\raw",
            "data\processed",
            "models\euromillions"
        )

        foreach ($path in $paths) {
            New-Item -ItemType Directory -Force -Path $path | Out-Null
        }
    }

    Invoke-Step "Bootstrap done. Launching UI..." {
        & $venvPython -m streamlit run "ui\streamlit_app.py"
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
