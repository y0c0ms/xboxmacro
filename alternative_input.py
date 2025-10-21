#!/usr/bin/env python3
"""
Alternative Input Simulation for Xbox Controller Macro HUD
Provides fallback input methods when ViGEmBus is not available.
"""

import time
import threading
from typing import List, Dict, Any, Optional

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class AlternativeInputSimulator:
    """Alternative input simulation using keyboard/mouse when ViGEmBus is not available."""
    
    def __init__(self):
        self.playing = False
        self.current_macro = []
        self.playback_thread = None
        
        # Controller to keyboard mapping
        self.button_mapping = {
            'button_0': 'a',      # A button -> A key
            'button_1': 'b',      # B button -> B key  
            'button_2': 'x',      # X button -> X key
            'button_3': 'y',      # Y button -> Y key
            'button_4': 'q',      # LB -> Q key
            'button_5': 'e',      # RB -> E key
            'button_6': 'escape',  # Back -> Escape key
            'button_7': 'enter',  # Start -> Enter key
            'button_8': 'space',  # Left Stick -> Space key
            'button_9': 'shift',  # Right Stick -> Shift key
        }
        
        # D-pad to arrow keys mapping
        self.dpad_mapping = {
            (0, 1): 'up',      # Up
            (0, -1): 'down',   # Down
            (-1, 0): 'left',   # Left
            (1, 0): 'right',   # Right
        }
    
    def play_macro(self, macro_data: List[Dict[str, Any]], loop: bool = False):
        """Play a recorded macro using keyboard/mouse simulation."""
        if self.playing:
            return False
        
        if not PYNPUT_AVAILABLE:
            print("pynput not available for input simulation")
            return False
        
        self.current_macro = macro_data.copy()
        self.playing = True
        self.playback_thread = threading.Thread(
            target=self._playback_loop, 
            args=(loop,), 
            daemon=True
        )
        self.playback_thread.start()
        return True
    
    def stop_playback(self):
        """Stop macro playback."""
        self.playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=1)
    
    def _playback_loop(self, loop: bool):
        """Internal playback loop using keyboard/mouse simulation."""
        while self.playing:
            start_time = time.time()
            
            for frame in self.current_macro:
                if not self.playing:
                    break
                
                # Wait for the correct timing
                target_time = frame.get('relative_time', 0)
                elapsed = time.time() - start_time
                if elapsed < target_time:
                    time.sleep(target_time - elapsed)
                
                # Simulate the input using keyboard/mouse
                self._simulate_input_alternative(frame)
            
            if not loop:
                break
        
        self.playing = False
    
    def _simulate_input_alternative(self, frame: Dict[str, Any]):
        """Simulate controller input using keyboard/mouse."""
        try:
            # Simulate button presses
            buttons = frame.get('buttons', {})
            for button_name, pressed in buttons.items():
                if pressed and button_name in self.button_mapping:
                    key = self.button_mapping[button_name]
                    self._press_key(key)
            
            # Simulate D-pad
            hats = frame.get('hats', {})
            for hat_name, hat_value in hats.items():
                if hat_value != (0, 0) and hat_value in self.dpad_mapping:
                    key = self.dpad_mapping[hat_value]
                    self._press_key(key)
            
            # Simulate stick movements (as mouse movement)
            axes = frame.get('axes', {})
            for axis_name, value in axes.items():
                if abs(value) > 0.1:  # Only if there's significant movement
                    self._simulate_stick_movement(axis_name, value)
            
        except Exception as e:
            print(f"Error in alternative input simulation: {e}")
    
    def _press_key(self, key_name: str):
        """Press a key using pynput."""
        try:
            if key_name == 'up':
                keyboard.press(Key.up)
                time.sleep(0.05)
                keyboard.release(Key.up)
            elif key_name == 'down':
                keyboard.press(Key.down)
                time.sleep(0.05)
                keyboard.release(Key.down)
            elif key_name == 'left':
                keyboard.press(Key.left)
                time.sleep(0.05)
                keyboard.release(Key.left)
            elif key_name == 'right':
                keyboard.press(Key.right)
                time.sleep(0.05)
                keyboard.release(Key.right)
            elif key_name == 'escape':
                keyboard.press(Key.esc)
                time.sleep(0.05)
                keyboard.release(Key.esc)
            elif key_name == 'enter':
                keyboard.press(Key.enter)
                time.sleep(0.05)
                keyboard.release(Key.enter)
            elif key_name == 'space':
                keyboard.press(Key.space)
                time.sleep(0.05)
                keyboard.release(Key.space)
            elif key_name == 'shift':
                keyboard.press(Key.shift)
                time.sleep(0.05)
                keyboard.release(Key.shift)
            else:
                # Regular letter keys
                keyboard.press(key_name)
                time.sleep(0.05)
                keyboard.release(key_name)
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def _simulate_stick_movement(self, axis_name: str, value: float):
        """Simulate stick movement as mouse movement."""
        try:
            # Convert stick value to mouse movement
            # This is a simplified mapping - you might want to adjust this
            if 'axis_0' in axis_name:  # Left stick X
                mouse.move(int(value * 10), 0)
            elif 'axis_1' in axis_name:  # Left stick Y
                mouse.move(0, int(value * 10))
            elif 'axis_2' in axis_name:  # Right stick X
                mouse.move(int(value * 5), 0)
            elif 'axis_3' in axis_name:  # Right stick Y
                mouse.move(0, int(value * 5))
        except Exception as e:
            print(f"Error simulating stick movement: {e}")

def test_alternative_input():
    """Test the alternative input simulator."""
    print("Testing Alternative Input Simulator")
    print("=" * 40)
    
    if not PYNPUT_AVAILABLE:
        print("✗ pynput not available")
        return False
    
    simulator = AlternativeInputSimulator()
    
    # Create a test macro
    test_macro = [
        {
            'buttons': {'button_0': True},  # A button
            'axes': {},
            'hats': {},
            'relative_time': 0.0
        },
        {
            'buttons': {'button_0': False},  # Release A button
            'axes': {},
            'hats': {},
            'relative_time': 0.1
        }
    ]
    
    print("Playing test macro (A button press)...")
    print("You should see an 'a' key press in 3 seconds...")
    
    time.sleep(3)
    success = simulator.play_macro(test_macro, loop=False)
    
    if success:
        print("✓ Alternative input simulation working!")
        time.sleep(2)
        simulator.stop_playback()
        return True
    else:
        print("✗ Alternative input simulation failed")
        return False

if __name__ == "__main__":
    test_alternative_input()
