#!/usr/bin/env python3
"""
Test script for Xbox Controller Macro HUD input simulation
Tests both virtual gamepad and alternative input methods.
"""

import sys
import time

def test_vigembus():
    """Test ViGEmBus virtual gamepad."""
    print("Testing ViGEmBus Virtual Gamepad...")
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        gamepad.reset()
        
        # Test button press
        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(0.1)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        
        print("✓ ViGEmBus virtual gamepad working!")
        return True
    except Exception as e:
        print(f"✗ ViGEmBus test failed: {e}")
        return False

def test_alternative_input():
    """Test alternative input simulation."""
    print("\nTesting Alternative Input Simulation...")
    try:
        from alternative_input import test_alternative_input
        return test_alternative_input()
    except Exception as e:
        print(f"✗ Alternative input test failed: {e}")
        return False

def main():
    """Run all input tests."""
    print("Xbox Controller Macro HUD - Input Test")
    print("=" * 50)
    
    vigembus_ok = test_vigembus()
    alternative_ok = test_alternative_input()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"ViGEmBus Virtual Gamepad: {'✓ Working' if vigembus_ok else '✗ Failed'}")
    print(f"Alternative Input (Keyboard/Mouse): {'✓ Working' if alternative_ok else '✗ Failed'}")
    
    if vigembus_ok:
        print("\n🎮 Virtual gamepad input simulation is working!")
        print("Your emulator should recognize macro inputs as controller input.")
    elif alternative_ok:
        print("\n⌨️ Alternative input simulation is working!")
        print("Macros will be simulated as keyboard/mouse input.")
        print("Note: Some emulators may not recognize this as controller input.")
    else:
        print("\n❌ No input simulation methods are working.")
        print("Please check the installation and try again.")
    
    print("\nYou can now use the Xbox Controller Macro HUD!")

if __name__ == "__main__":
    main()
