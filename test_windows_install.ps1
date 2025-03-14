# Test script for Windows installation
Write-Host "Testing Version Finder installation on Windows" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.6 or higher." -ForegroundColor Red
    exit 1
}

# Check pip installation
try {
    $pipVersion = pip --version
    Write-Host "Pip detected: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: pip not found. Please ensure pip is installed." -ForegroundColor Red
    exit 1
}

# Check if Make is available
$makeAvailable = $false
try {
    $makeVersion = make --version
    Write-Host "Make detected: $makeVersion" -ForegroundColor Green
    $makeAvailable = $true
} catch {
    Write-Host "Make not detected. You can use the alternative installation methods." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation options available:" -ForegroundColor Cyan
if ($makeAvailable) {
    Write-Host "1. Using Make: 'make install'" -ForegroundColor Green
}
Write-Host "2. Using Batch script: 'install.bat'" -ForegroundColor Green
Write-Host "3. Using PowerShell script: '.\install.ps1'" -ForegroundColor Green
Write-Host ""

Write-Host "All prerequisites checked. You can proceed with installation." -ForegroundColor Green 