@echo off
setlocal enabledelayedexpansion

echo Version Finder Installation Script for Windows
echo ==============================================
echo.
echo Choose an installation option:
echo 1. Only core
echo 2. Core + CLI
echo 3. Core + GUI
echo 4. Core + GUI + CLI
echo 5. Development installation (all components with dev dependencies)
echo.

set /p choice="Enter your choice [1-5]: "

if "%choice%"=="1" (
    call :install_core
) else if "%choice%"=="2" (
    call :install_cli
) else if "%choice%"=="3" (
    call :install_gui
) else if "%choice%"=="4" (
    call :install_gui
    call :install_cli
) else if "%choice%"=="5" (
    call :install_dev
) else if /i "%choice%"=="clean" (
    call :clean
) else (
    echo Invalid choice. Exiting.
    exit /b 1
)

echo.
echo Installation completed successfully!
exit /b 0

:install_core
echo Installing core component...
pip install core\
exit /b 0

:install_cli
echo Installing CLI component...
call :install_core
pip install cli\
exit /b 0

:install_gui
echo Installing GUI component...
call :install_core
pip install gui\
exit /b 0

:install_dev
echo Installing development environment...
pip install -e core\[dev]
pip install -e cli\
pip install -e gui\
exit /b 0

:clean
echo Cleaning up...
powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__','build','dist','*.egg-info' | Where-Object { $_.FullName -notmatch '\.venv' } | Remove-Item -Recurse -Force"
if exist htmlcov rmdir /s /q htmlcov
if exist .coverage del /f .coverage
exit /b 0 