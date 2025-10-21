
@echo off
echo Xbox Controller Macro HUD Launcher
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if ViGEmBus is needed
echo Checking for ViGEmBus driver...
python -c "import vgamepad; vg = vgamepad.VX360Gamepad(); vg.reset(); print('ViGEmBus OK')" 2>nul
if errorlevel 1 (
    echo.
    echo ViGEmBus driver not detected. Installing...
    echo This may require Administrator privileges.
    echo.
    python install_vigembus.py
    echo.
    echo If installation failed, please run as Administrator.
    echo.
)

REM Run the launcher script
python run_macro_hud.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
