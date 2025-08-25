# Build script for UACalc (PowerShell)

# Stop on first error
$ErrorActionPreference = "Stop"

# Parse command line arguments
param(
    [switch]$Release
)

Write-Host "Building UACalc..." -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Virtual environment not activated. Activating..." -ForegroundColor Yellow
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to activate virtual environment." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
        exit 1
    }
}

# Check if maturin is available
try {
    $maturinVersion = maturin --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "maturin not found"
    }
    Write-Host "Found maturin: $maturinVersion" -ForegroundColor Green
} catch {
    Write-Host "maturin not found. Installing..." -ForegroundColor Yellow
    cargo install maturin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install maturin." -ForegroundColor Red
        exit 1
    }
}

# Build the Rust extension
Write-Host "Building Rust extension..." -ForegroundColor Yellow
if ($Release) {
    maturin build --release
} else {
    maturin build
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Rust extension." -ForegroundColor Red
    exit 1
}

# Install the extension in development mode
Write-Host "Installing extension in development mode..." -ForegroundColor Yellow
maturin develop
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install extension in development mode." -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest tests/python/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed." -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully!" -ForegroundColor Green
