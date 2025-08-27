# Setup script for UACalc development environment (PowerShell)

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "Setting up UACalc development environment..." -ForegroundColor Green

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Rust
Write-Host "Checking Rust installation..." -ForegroundColor Yellow
try {
    $rustVersion = rustc --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Rust not found"
    }
    Write-Host "Found: $rustVersion" -ForegroundColor Green
}
catch {
    Write-Host "Rust not found. Please install Rust from https://rustup.rs" -ForegroundColor Red
    Write-Host "Run: winget install Rust.Rust or visit https://rustup.rs" -ForegroundColor Yellow
    exit 1
}

# Install maturin if not present
try {
    $maturinVersion = maturin --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "maturin not found"
    }
    Write-Host "Found maturin: $maturinVersion" -ForegroundColor Green
}
catch {
    Write-Host "Installing maturin via pip..." -ForegroundColor Yellow
    python -m pip install maturin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install maturin via pip. Trying cargo install..." -ForegroundColor Yellow
        cargo install maturin --force
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install maturin." -ForegroundColor Red
            exit 1
        }
    }
}

# Install Python dependencies from uacalc-py directory
Write-Host "Installing Python dependencies from uacalc-py..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upgrade pip." -ForegroundColor Red
    exit 1
}

# Change to uacalc-py directory and install in editable mode
Push-Location uacalc-py
python -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install package in editable mode." -ForegroundColor Red
    Pop-Location
    exit 1
}

python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install development dependencies." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Build Rust extension: cd uacalc-py && maturin develop" -ForegroundColor White
Write-Host "3. Run tests: python -m pytest tests/python/" -ForegroundColor White
Write-Host ""
Write-Host "Note: Always run maturin commands from the uacalc-py directory!" -ForegroundColor Yellow
