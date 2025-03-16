# Version Finder Installation Script for Windows (PowerShell)
Write-Host "Version Finder Installation Script for Windows" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose an installation option:"
Write-Host "1. Only core"
Write-Host "2. Core + CLI"
Write-Host "3. Core + GUI"
Write-Host "4. Core + GUI + CLI"
Write-Host "5. Development installation (all components with dev dependencies)"
Write-Host "6. Clean project files"
Write-Host ""

$choice = Read-Host "Enter your choice [1-6]"

function Install-Core {
    Write-Host "Installing core component..." -ForegroundColor Green
    pip install .\core\
}

function Install-CLI {
    Write-Host "Installing CLI component..." -ForegroundColor Green
    Install-Core
    pip install .\cli\
}

function Install-GUI {
    Write-Host "Installing GUI component..." -ForegroundColor Green
    Install-Core
    pip install .\gui\
}

function Install-Dev {
    Write-Host "Installing development environment..." -ForegroundColor Green
    pip install -e .\core\[dev]
    pip install -e .\cli\
    pip install -e .\gui\[gui]
}

function Clean-Project {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__','build','dist','*.egg-info' | 
        Where-Object { $_.FullName -notmatch '\.venv' } | 
        Remove-Item -Recurse -Force
    
    if (Test-Path htmlcov) { Remove-Item -Recurse -Force htmlcov }
    if (Test-Path .coverage) { Remove-Item -Force .coverage }
}

switch ($choice) {
    "1" { Install-Core }
    "2" { Install-CLI }
    "3" { Install-GUI }
    "4" { 
        Install-GUI
        Install-CLI 
    }
    "5" { Install-Dev }
    "6" { Clean-Project }
    "clean" { Clean-Project }
    default { 
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1 
    }
}

Write-Host ""
Write-Host "Installation completed successfully!" -ForegroundColor Green 