#!/usr/bin/env python3
"""
Xbox Macro HUD Launcher
Simple launcher script for the Xbox Controller Macro HUD application.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pygame
        import tkinter
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def main():
    """Main launcher function."""
    print("Xbox Controller Macro HUD Launcher")
    print("=" * 40)
    
    # Check if dependencies are installed
    if not check_dependencies():
        print("\nDependencies not found. Installing...")
        if not install_dependencies():
            print("Failed to install dependencies. Please install manually:")
            print("pip install pygame")
            return 1
    
    # Check if main script exists
    if not os.path.exists("xbox_macro_hud.py"):
        print("Error: xbox_macro_hud.py not found!")
        print("Make sure you're running this from the correct directory.")
        return 1
    
    # Launch the main application
    print("\nStarting Xbox Controller Macro HUD...")
    try:
        import xbox_macro_hud
        xbox_macro_hud.main()
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
