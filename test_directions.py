#!/usr/bin/env python3
"""
Test script to verify joystick directions are correct
Tests each direction individually to ensure proper mapping.
"""

import time
import sys

def test_directions():
    """Test each joystick direction individually."""
    print("Testing Joystick Directions")
    print("=" * 40)
    print("This will test each direction for 2 seconds.")
    print("Watch your game/emulator to see if directions are correct.")
    print()
    
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        
        print("✓ Virtual gamepad initialized")
        print()
        
        # Test left stick directions
        print("Testing LEFT STICK directions:")
        
        directions = [
            ("UP", 0, -32767),
            ("DOWN", 0, 32767),
            ("LEFT", -32767, 0),
            ("RIGHT", 32767, 0)
        ]
        
        for direction, x, y in directions:
            print(f"  Moving {direction} for 2 seconds...")
            gamepad.left_joystick(x_value=x, y_value=y)
            gamepad.update()
            time.sleep(2)
            
            # Center
            gamepad.left_joystick(x_value=0, y_value=0)
            gamepad.update()
            time.sleep(0.5)
        
        print()
        print("Testing RIGHT STICK directions:")
        
        for direction, x, y in directions:
            print(f"  Moving {direction} for 2 seconds...")
            gamepad.right_joystick(x_value=x, y_value=y)
            gamepad.update()
            time.sleep(2)
            
            # Center
            gamepad.right_joystick(x_value=0, y_value=0)
            gamepad.update()
            time.sleep(0.5)
        
        print()
        print("✓ Direction test completed!")
        print("Check if the directions in your game match the expected directions.")
        
        return True
        
    except Exception as e:
        print(f"✗ Direction test failed: {e}")
        return False

def test_diagonal_directions():
    """Test diagonal directions."""
    print("\nTesting Diagonal Directions")
    print("=" * 30)
    
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        
        diagonals = [
            ("UP-LEFT", -32767, -32767),
            ("UP-RIGHT", 32767, -32767),
            ("DOWN-LEFT", -32767, 32767),
            ("DOWN-RIGHT", 32767, 32767)
        ]
        
        for direction, x, y in diagonals:
            print(f"  Moving {direction} for 2 seconds...")
            gamepad.left_joystick(x_value=x, y_value=y)
            gamepad.update()
            time.sleep(2)
            
            # Center
            gamepad.left_joystick(x_value=0, y_value=0)
            gamepad.update()
            time.sleep(0.5)
        
        print("✓ Diagonal test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Diagonal test failed: {e}")
        return False

def main():
    """Run direction tests."""
    print("Xbox Controller Macro HUD - Direction Test")
    print("=" * 50)
    print("This will test joystick directions to verify they're correct.")
    print("Make sure your game/emulator is running and focused.")
    print()
    
    input("Press Enter to start the direction test...")
    
    # Test basic directions
    basic_ok = test_directions()
    
    # Test diagonal directions
    diagonal_ok = test_diagonal_directions()
    
    print("\n" + "=" * 50)
    print("Direction Test Results:")
    print(f"Basic Directions: {'✓ Working' if basic_ok else '✗ Failed'}")
    print(f"Diagonal Directions: {'✓ Working' if diagonal_ok else '✗ Failed'}")
    
    if basic_ok and diagonal_ok:
        print("\n🎮 Direction test completed!")
        print("If the directions were correct in your game, the joystick mapping is fixed.")
        print("If not, we may need to adjust the axis mapping further.")
    else:
        print("\n❌ Direction test failed.")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main()
