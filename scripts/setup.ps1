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

# Create virtual environment
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}
else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upgrade pip." -ForegroundColor Red
    exit 1
}

python -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install package in editable mode." -ForegroundColor Red
    exit 1
}

python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install development dependencies." -ForegroundColor Red
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
    Write-Host "Installing maturin..." -ForegroundColor Yellow
    cargo install maturin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install maturin." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Build Rust extension: maturin develop" -ForegroundColor White
Write-Host "3. Run tests: python -m pytest tests/python/" -ForegroundColor White
