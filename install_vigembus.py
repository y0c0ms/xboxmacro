#!/usr/bin/env python3
"""
ViGEmBus Driver Installer for Xbox Controller Macro HUD
Downloads and installs the required ViGEmBus driver for vgamepad functionality.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path

def download_file(url, filename):
    """Download a file from URL."""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def install_vigembus():
    """Install ViGEmBus driver."""
    print("ViGEmBus Driver Installation")
    print("=" * 40)
    
    # Check if already installed with more thorough testing
    try:
        import vgamepad as vg
        test_gamepad = vg.VX360Gamepad()
        test_gamepad.reset()
        # Try to actually use the gamepad
        test_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        test_gamepad.update()
        test_gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        test_gamepad.update()
        print("✓ ViGEmBus is properly installed and working!")
        return True
    except Exception as e:
        print(f"ViGEmBus test failed: {e}")
        print("Proceeding with installation...")
    
    # ViGEmBus download URLs (official releases)
    vigembus_urls = [
        "https://github.com/ViGEm/ViGEmBus/releases/latest/download/ViGEmBus_Setup_x64.exe",
        "https://github.com/ViGEm/ViGEmBus/releases/download/v1.21.442/ViGEmBus_Setup_x64.exe"
    ]
    
    installer_name = "ViGEmBus_Setup_x64.exe"
    
    # Try to download the installer
    success = False
    for url in vigembus_urls:
        if download_file(url, installer_name):
            success = True
            break
    
    if not success:
        print("\n✗ Failed to download ViGEmBus installer.")
        print("Please download manually from:")
        print("https://github.com/ViGEm/ViGEmBus/releases/latest")
        print("\nThen run the installer as Administrator.")
        return False
    
    # Run the installer
    print(f"\nRunning {installer_name}...")
    print("Note: You may need to run this script as Administrator.")
    
    try:
        # Try to run the installer
        result = subprocess.run([installer_name, "/S"], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✓ ViGEmBus installer completed successfully!")
        else:
            print(f"⚠ Installer returned code {result.returncode}")
            print("You may need to run the installer manually as Administrator.")
            
    except subprocess.TimeoutExpired:
        print("⚠ Installer timed out, but may have completed.")
    except Exception as e:
        print(f"⚠ Error running installer: {e}")
        print("Please run the installer manually as Administrator.")
    
    # Clean up
    try:
        os.remove(installer_name)
    except:
        pass
    
    # Test installation with multiple attempts
    print("\nTesting ViGEmBus installation...")
    for attempt in range(3):
        try:
            import vgamepad as vg
            test_gamepad = vg.VX360Gamepad()
            test_gamepad.reset()
            # Try to actually use the gamepad
            test_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            test_gamepad.update()
            test_gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            test_gamepad.update()
            print("✓ ViGEmBus is now working!")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                print("Retrying in 2 seconds...")
                import time
                time.sleep(2)
    
    print(f"✗ ViGEmBus test failed after 3 attempts")
    print("\nTroubleshooting steps:")
    print("1. Restart your computer (REQUIRED after driver installation)")
    print("2. Run this script as Administrator")
    print("3. Check Windows Device Manager for ViGEm devices")
    print("4. Download ViGEmBus manually from:")
    print("   https://github.com/ViGEm/ViGEmBus/releases/latest")
    print("5. Uninstall and reinstall ViGEmBus if needed")
    return False

def main():
    """Main installation function."""
    print("Xbox Controller Macro HUD - ViGEmBus Installer")
    print("=" * 50)
    print("This will install the ViGEmBus driver required for virtual gamepad functionality.")
    print()
    
    # Check if running as administrator (Windows)
    if os.name == 'nt':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("⚠ Warning: Not running as Administrator.")
                print("You may need to run this script as Administrator for proper installation.")
                print()
        except:
            pass
    
    success = install_vigembus()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ ViGEmBus installation completed successfully!")
        print("You can now use the Xbox Controller Macro HUD with full input simulation.")
    else:
        print("✗ ViGEmBus installation failed or incomplete.")
        print("Please install ViGEmBus manually:")
        print("1. Download from: https://github.com/ViGEm/ViGEmBus/releases/latest")
        print("2. Run the installer as Administrator")
        print("3. Restart your computer")
        print("4. Test the Xbox Controller Macro HUD again")

if __name__ == "__main__":
    main()
