#!/usr/bin/env python3
"""
Dependency installer for Xbox Controller Macro HUD
Installs required packages for controller input simulation.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    """Install all required dependencies."""
    print("Xbox Controller Macro HUD - Dependency Installer")
    print("=" * 50)
    
    # Required packages
    packages = [
        "pygame>=2.5.0",
        "vgamepad>=0.0.6", 
        "pynput>=1.7.6"
    ]
    
    print("Installing required packages...")
    print()
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 50)
    if success_count == len(packages):
        print("✓ All dependencies installed successfully!")
        print()
        print("You can now run the Xbox Controller Macro HUD:")
        print("  python xbox_macro_hud.py")
        print("  or")
        print("  python run_macro_hud.py")
    else:
        print(f"⚠ {len(packages) - success_count} packages failed to install.")
        print("Please install them manually:")
        for package in packages:
            print(f"  pip install {package}")
        print()
        print("Note: vgamepad may require Visual C++ Redistributable on Windows.")
        print("Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")

if __name__ == "__main__":
    main()
