# Build script for UACalc (PowerShell)

# Stop on first error
$ErrorActionPreference = "Stop"

# Parse command line arguments
param(
    [switch]$Release
)

Write-Host "Building UACalc..." -ForegroundColor Green

# Check if maturin is available
try {
    $maturinVersion = maturin --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "maturin not found"
    }
    Write-Host "Found maturin: $maturinVersion" -ForegroundColor Green
}
catch {
    Write-Host "maturin not found. Installing via pip..." -ForegroundColor Yellow
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

# Change to uacalc-py directory where the Python package is located
Write-Host "Changing to uacalc-py directory..." -ForegroundColor Yellow
Push-Location uacalc-py

# Build the Rust extension
Write-Host "Building Rust extension..." -ForegroundColor Yellow
if ($Release) {
    maturin build --release
}
else {
    maturin build
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Rust extension." -ForegroundColor Red
    Pop-Location
    exit 1
}

# Install the extension in development mode
Write-Host "Installing extension in development mode..." -ForegroundColor Yellow
maturin develop
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install extension in development mode." -ForegroundColor Red
    Pop-Location
    exit 1
}

# Return to root directory
Pop-Location

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest tests/python/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed." -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully!" -ForegroundColor Green
