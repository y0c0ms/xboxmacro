#!/usr/bin/env python3
"""
Test script for joystick movement in Xbox Controller Macro HUD
Tests joystick input simulation with virtual gamepad.
"""

import time
import sys

def test_joystick_movement():
    """Test joystick movement simulation."""
    print("Testing Joystick Movement Simulation")
    print("=" * 40)
    
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        
        print("✓ Virtual gamepad initialized")
        
        # Test left stick movement
        print("Testing left stick movement...")
        
        # Move left stick up
        print("  Moving left stick UP...")
        gamepad.left_joystick(x_value=0, y_value=-32767)
        gamepad.update()
        time.sleep(1)
        
        # Move left stick right
        print("  Moving left stick RIGHT...")
        gamepad.left_joystick(x_value=32767, y_value=0)
        gamepad.update()
        time.sleep(1)
        
        # Move left stick down
        print("  Moving left stick DOWN...")
        gamepad.left_joystick(x_value=0, y_value=32767)
        gamepad.update()
        time.sleep(1)
        
        # Move left stick left
        print("  Moving left stick LEFT...")
        gamepad.left_joystick(x_value=-32767, y_value=0)
        gamepad.update()
        time.sleep(1)
        
        # Center the stick
        print("  Centering left stick...")
        gamepad.left_joystick(x_value=0, y_value=0)
        gamepad.update()
        time.sleep(1)
        
        # Test right stick movement
        print("Testing right stick movement...")
        
        # Move right stick up
        print("  Moving right stick UP...")
        gamepad.right_joystick(x_value=0, y_value=-32767)
        gamepad.update()
        time.sleep(1)
        
        # Move right stick right
        print("  Moving right stick RIGHT...")
        gamepad.right_joystick(x_value=32767, y_value=0)
        gamepad.update()
        time.sleep(1)
        
        # Move right stick down
        print("  Moving right stick DOWN...")
        gamepad.right_joystick(x_value=0, y_value=32767)
        gamepad.update()
        time.sleep(1)
        
        # Move right stick left
        print("  Moving right stick LEFT...")
        gamepad.right_joystick(x_value=-32767, y_value=0)
        gamepad.update()
        time.sleep(1)
        
        # Center the stick
        print("  Centering right stick...")
        gamepad.right_joystick(x_value=0, y_value=0)
        gamepad.update()
        
        print("✓ Joystick movement test completed!")
        print("Check if your game/emulator detects the joystick movement.")
        
        return True
        
    except Exception as e:
        print(f"✗ Joystick test failed: {e}")
        return False

def test_diagonal_movement():
    """Test diagonal joystick movement."""
    print("\nTesting Diagonal Movement")
    print("=" * 30)
    
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        
        # Test diagonal movements
        diagonals = [
            ("Up-Left", -32767, -32767),
            ("Up-Right", 32767, -32767),
            ("Down-Left", -32767, 32767),
            ("Down-Right", 32767, 32767)
        ]
        
        for direction, x, y in diagonals:
            print(f"  Moving {direction}...")
            gamepad.left_joystick(x_value=x, y_value=y)
            gamepad.update()
            time.sleep(0.5)
        
        # Center
        gamepad.left_joystick(x_value=0, y_value=0)
        gamepad.update()
        
        print("✓ Diagonal movement test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Diagonal movement test failed: {e}")
        return False

def main():
    """Run joystick tests."""
    print("Xbox Controller Macro HUD - Joystick Test")
    print("=" * 50)
    print("This will test joystick movement simulation.")
    print("Make sure your game/emulator is running to see the movement.")
    print()
    
    input("Press Enter to start the test...")
    
    # Test basic joystick movement
    basic_ok = test_joystick_movement()
    
    # Test diagonal movement
    diagonal_ok = test_diagonal_movement()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Basic Joystick Movement: {'✓ Working' if basic_ok else '✗ Failed'}")
    print(f"Diagonal Movement: {'✓ Working' if diagonal_ok else '✗ Failed'}")
    
    if basic_ok and diagonal_ok:
        print("\n🎮 Joystick movement simulation is working!")
        print("Your macros should now be able to move characters properly.")
    else:
        print("\n❌ Joystick movement simulation has issues.")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main()
