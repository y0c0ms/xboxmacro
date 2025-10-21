#!/usr/bin/env python3
"""
Xbox Controller Macro HUD
A comprehensive application for recording, editing, and playing macros for Xbox controllers.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import json
import time
import threading
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

# Try to import input simulation libraries
try:
    import vgamepad as vg
    VGAMEPAD_AVAILABLE = True
except ImportError:
    VGAMEPAD_AVAILABLE = False
    print("Warning: vgamepad not available. Input simulation will be limited.")

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available. Some input simulation features may be limited.")

# Import alternative input simulator
try:
    from alternative_input import AlternativeInputSimulator
    ALTERNATIVE_INPUT_AVAILABLE = True
except ImportError:
    ALTERNATIVE_INPUT_AVAILABLE = False

class XboxController:
    """Handles Xbox controller input detection and management."""
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self.controller_connected = False
        self.connect_controller()
    
    def connect_controller(self):
        """Attempt to connect to an Xbox controller."""
        try:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.controller_connected = True
                return True
        except Exception as e:
            print(f"Controller connection error: {e}")
        return False
    
    def get_controller_state(self) -> Dict[str, Any]:
        """Get current controller state including buttons, axes, and triggers."""
        if not self.controller_connected or not self.joystick:
            return {}
        
        pygame.event.pump()
        
        # Button states (0-15 for Xbox controller)
        buttons = {}
        for i in range(self.joystick.get_numbuttons()):
            buttons[f"button_{i}"] = self.joystick.get_button(i)
        
        # Axis states (left stick, right stick, triggers)
        axes = {}
        for i in range(self.joystick.get_numaxes()):
            axes[f"axis_{i}"] = round(self.joystick.get_axis(i), 3)
        
        # Hat states (D-pad)
        hats = {}
        for i in range(self.joystick.get_numhats()):
            hats[f"hat_{i}"] = self.joystick.get_hat(i)
        
        return {
            'buttons': buttons,
            'axes': axes,
            'hats': hats,
            'timestamp': time.time()
        }
    
    def get_button_name(self, button_id: int) -> str:
        """Convert button ID to readable name."""
        button_names = {
            0: "A", 1: "B", 2: "X", 3: "Y",
            4: "LB", 5: "RB", 6: "Back", 7: "Start",
            8: "Left Stick", 9: "Right Stick"
        }
        return button_names.get(button_id, f"Button {button_id}")

class MacroRecorder:
    """Handles macro recording functionality."""
    
    def __init__(self, controller: XboxController):
        self.controller = controller
        self.recording = False
        self.macro_data = []
        self.start_time = None
    
    def start_recording(self):
        """Start recording macro."""
        self.recording = True
        self.macro_data = []
        self.start_time = time.time()
    
    def stop_recording(self):
        """Stop recording macro."""
        self.recording = False
        return self.macro_data.copy()
    
    def update_recording(self):
        """Update recording with current controller state."""
        if not self.recording:
            return
        
        state = self.controller.get_controller_state()
        if state:
            # Record all states, not just when there's input
            # This ensures we capture the full sequence including releases
            state['relative_time'] = time.time() - self.start_time
            self.macro_data.append(state)

class MacroPlayer:
    """Handles macro playback functionality."""
    
    def __init__(self, controller: XboxController):
        self.controller = controller
        self.playing = False
        self.current_macro = []
        self.playback_thread = None
        
        # Initialize virtual gamepad if available
        self.virtual_gamepad = None
        self.vigembus_available = False
        self.alternative_simulator = None
        
        # Track current joystick states
        self.current_left_stick = (0, 0)  # (x, y)
        self.current_right_stick = (0, 0)  # (x, y)
        
        # Axis mapping configuration - adjust these if directions are wrong
        self.axis_mapping = {
            'invert_x': False,  # Set to True if X axis is inverted
            'invert_y': True,   # Set to True if Y axis is inverted
            'swap_xy': False,   # Set to True if X and Y are swapped
        }
        
        if VGAMEPAD_AVAILABLE:
            try:
                self.virtual_gamepad = vg.VX360Gamepad()
                # Test if ViGEmBus is working
                self.virtual_gamepad.reset()
                self.vigembus_available = True
                print("Virtual gamepad initialized successfully")
            except Exception as e:
                print(f"Failed to initialize virtual gamepad: {e}")
                print("This usually means ViGEmBus driver is not installed.")
                print("Run 'python install_vigembus.py' to install the required driver.")
                self.virtual_gamepad = None
                self.vigembus_available = False
                
                # Initialize alternative input simulator as fallback
                if ALTERNATIVE_INPUT_AVAILABLE:
                    try:
                        self.alternative_simulator = AlternativeInputSimulator()
                        print("Alternative input simulator initialized as fallback")
                    except Exception as e:
                        print(f"Failed to initialize alternative input simulator: {e}")
                        self.alternative_simulator = None
    
    def play_macro(self, macro_data: List[Dict[str, Any]], loop: bool = False):
        """Play a recorded macro."""
        if self.playing:
            return False
        
        # Choose the best available input method
        if self.vigembus_available and self.virtual_gamepad:
            print("Using virtual gamepad for input simulation")
            self.current_macro = macro_data.copy()
            self.playing = True
            self.playback_thread = threading.Thread(
                target=self._playback_loop, 
                args=(loop,), 
                daemon=True
            )
            self.playback_thread.start()
            return True
        elif self.alternative_simulator:
            print("Using alternative input simulation (keyboard/mouse)")
            return self.alternative_simulator.play_macro(macro_data, loop)
        else:
            print("No input simulation method available")
            return False
    
    def stop_playback(self):
        """Stop macro playback."""
        self.playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=1)
        
        # Also stop alternative simulator if running
        if self.alternative_simulator:
            self.alternative_simulator.stop_playback()
    
    def _playback_loop(self, loop: bool):
        """Internal playback loop."""
        while self.playing:
            start_time = time.time()
            
            # Reset joysticks at the start of playback
            self.reset_joysticks()
            
            for frame in self.current_macro:
                if not self.playing:
                    break
                
                # Wait for the correct timing
                target_time = frame.get('relative_time', 0)
                elapsed = time.time() - start_time
                if elapsed < target_time:
                    time.sleep(target_time - elapsed)
                
                # Simulate the input
                self._simulate_input(frame)
            
            if not loop:
                break
        
        # Reset joysticks when playback ends
        self.reset_joysticks()
        self.playing = False
    
    def _simulate_input(self, frame: Dict[str, Any]):
        """Simulate controller input using virtual gamepad."""
        if not self.virtual_gamepad:
            print(f"Virtual gamepad not available. Would simulate: {frame}")
            return
        
        try:
            # Reset all inputs first
            self.virtual_gamepad.reset()
            
            # Set button states
            buttons = frame.get('buttons', {})
            for button_name, pressed in buttons.items():
                if pressed:
                    button_id = int(button_name.split('_')[1])
                    self._set_button(button_id, True)
            
            # Set axis values (sticks and triggers)
            axes = frame.get('axes', {})
            for axis_name, value in axes.items():
                axis_id = int(axis_name.split('_')[1])
                self._set_axis(axis_id, value)
            
            # Set hat values (D-pad)
            hats = frame.get('hats', {})
            for hat_name, hat_value in hats.items():
                hat_id = int(hat_name.split('_')[1])
                self._set_hat(hat_id, hat_value)
            
            # Update the virtual gamepad
            self.virtual_gamepad.update()
            
        except Exception as e:
            print(f"Error simulating input: {e}")
    
    def reset_joysticks(self):
        """Reset joystick positions to center."""
        if self.virtual_gamepad:
            try:
                self.current_left_stick = (0, 0)
                self.current_right_stick = (0, 0)
                self.virtual_gamepad.left_joystick(x_value=0, y_value=0)
                self.virtual_gamepad.right_joystick(x_value=0, y_value=0)
                self.virtual_gamepad.update()
            except Exception as e:
                print(f"Error resetting joysticks: {e}")
    
    def _set_button(self, button_id: int, pressed: bool):
        """Set button state on virtual gamepad."""
        button_map = {
            0: self.virtual_gamepad.press_button,  # A
            1: self.virtual_gamepad.press_button,  # B
            2: self.virtual_gamepad.press_button,  # X
            3: self.virtual_gamepad.press_button,  # Y
            4: self.virtual_gamepad.press_button,  # LB
            5: self.virtual_gamepad.press_button,  # RB
            6: self.virtual_gamepad.press_button,  # Back
            7: self.virtual_gamepad.press_button,  # Start
            8: self.virtual_gamepad.press_button,  # Left Stick
            9: self.virtual_gamepad.press_button,  # Right Stick
        }
        
        if button_id in button_map and pressed:
            # Map to vgamepad button constants
            vg_buttons = {
                0: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
                1: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
                2: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
                3: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
                4: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
                5: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
                6: vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
                7: vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
                8: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
                9: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            }
            
            if button_id in vg_buttons:
                self.virtual_gamepad.press_button(vg_buttons[button_id])
    
    def _set_axis(self, axis_id: int, value: float):
        """Set axis value on virtual gamepad."""
        # Clamp value to valid range
        value = max(-1.0, min(1.0, value))
        
        try:
            # Apply axis mapping configuration
            if self.axis_mapping['invert_x'] and axis_id in [0, 2]:  # X axes
                value = -value
            if self.axis_mapping['invert_y'] and axis_id in [1, 3]:  # Y axes
                value = -value
            
            # Convert to vgamepad range (-32768 to 32767)
            vg_value = int(value * 32767)
            
            
            
            # Set axis values based on configuration
            if axis_id == 0:  # Left stick X
                if self.axis_mapping['swap_xy']:
                    self.current_left_stick = (self.current_left_stick[0], vg_value)
                else:
                    self.current_left_stick = (vg_value, self.current_left_stick[1])
                self.virtual_gamepad.left_joystick(x_value=self.current_left_stick[0], y_value=self.current_left_stick[1])
            elif axis_id == 1:  # Left stick Y
                if self.axis_mapping['swap_xy']:
                    self.current_left_stick = (vg_value, self.current_left_stick[1])
                else:
                    self.current_left_stick = (self.current_left_stick[0], vg_value)
                self.virtual_gamepad.left_joystick(x_value=self.current_left_stick[0], y_value=self.current_left_stick[1])
            elif axis_id == 2:  # Right stick X
                if self.axis_mapping['swap_xy']:
                    self.current_right_stick = (self.current_right_stick[0], vg_value)
                else:
                    self.current_right_stick = (vg_value, self.current_right_stick[1])
                self.virtual_gamepad.right_joystick(x_value=self.current_right_stick[0], y_value=self.current_right_stick[1])
            elif axis_id == 3:  # Right stick Y
                if self.axis_mapping['swap_xy']:
                    self.current_right_stick = (vg_value, self.current_right_stick[1])
                else:
                    self.current_right_stick = (self.current_right_stick[0], vg_value)
                self.virtual_gamepad.right_joystick(x_value=self.current_right_stick[0], y_value=self.current_right_stick[1])
            elif axis_id == 4:  # Left trigger
                self.virtual_gamepad.left_trigger = int((value + 1) * 127.5)
            elif axis_id == 5:  # Right trigger
                self.virtual_gamepad.right_trigger = int((value + 1) * 127.5)
        except Exception as e:
            print(f"Error setting axis {axis_id} to {value}: {e}")
    
    def _set_hat(self, hat_id: int, hat_value: tuple):
        """Set hat (D-pad) value on virtual gamepad."""
        if hat_id == 0:  # D-pad
            x, y = hat_value
            if x == -1:  # Left
                self.virtual_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            elif x == 1:  # Right
                self.virtual_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            if y == -1:  # Down
                self.virtual_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            elif y == 1:  # Up
                self.virtual_gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)

class MacroEditor:
    """Handles macro editing functionality."""
    
    def __init__(self):
        self.macros = {}
        self.current_macro = None
    
    def create_macro(self, name: str, data: List[Dict[str, Any]]):
        """Create a new macro."""
        self.macros[name] = {
            'name': name,
            'data': data,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat()
        }
    
    def edit_macro(self, name: str, new_data: List[Dict[str, Any]]):
        """Edit an existing macro."""
        if name in self.macros:
            self.macros[name]['data'] = new_data
            self.macros[name]['modified'] = datetime.now().isoformat()
    
    def delete_macro(self, name: str):
        """Delete a macro."""
        if name in self.macros:
            del self.macros[name]
    
    def get_macro(self, name: str) -> Optional[Dict[str, Any]]:
        """Get macro data."""
        return self.macros.get(name)
    
    def list_macros(self) -> List[str]:
        """List all macro names."""
        return list(self.macros.keys())
    
    def save_macros(self, filename: str):
        """Save macros to file."""
        with open(filename, 'w') as f:
            json.dump(self.macros, f, indent=2)
    
    def load_macros(self, filename: str):
        """Load macros from file."""
        try:
            with open(filename, 'r') as f:
                self.macros = json.load(f)
        except Exception as e:
            print(f"Error loading macros: {e}")

class XboxMacroHUD:
    """Main HUD application for Xbox controller macros."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Xbox Controller Macro HUD")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize components
        self.controller = XboxController()
        self.recorder = MacroRecorder(self.controller)
        self.player = MacroPlayer(self.controller)
        self.editor = MacroEditor()
        
        # GUI state
        self.recording = False
        self.playing = False
        self.current_macro_name = ""
        
        self.setup_gui()
        self.setup_controller_monitoring()
    
    def setup_gui(self):
        """Setup the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Xbox Controller Macro HUD", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Controller status
        self.status_label = ttk.Label(main_frame, text="Controller: Not Connected", 
                                     foreground='red')
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(0, 5))
        
        # Input simulation status
        if VGAMEPAD_AVAILABLE and self.player.vigembus_available:
            vg_status = "Virtual Gamepad Available (ViGEmBus OK)"
            vg_color = 'green'
        elif VGAMEPAD_AVAILABLE and not self.player.vigembus_available and self.player.alternative_simulator:
            vg_status = "Alternative Input Available (Keyboard/Mouse)"
            vg_color = 'orange'
        elif VGAMEPAD_AVAILABLE and not self.player.vigembus_available:
            vg_status = "ViGEmBus Driver Required"
            vg_color = 'red'
        else:
            vg_status = "No Input Simulation Available"
            vg_color = 'red'
            
        self.vg_status_label = ttk.Label(main_frame, text=f"Input Simulation: {vg_status}", 
                                         foreground=vg_color)
        self.vg_status_label.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        # Installation help button
        if VGAMEPAD_AVAILABLE and not self.player.vigembus_available:
            self.install_button = ttk.Button(main_frame, text="Install ViGEmBus Driver", 
                                           command=self.show_vigembus_help)
            self.install_button.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        else:
            self.install_button = None
        
        # Recording section
        record_frame = ttk.LabelFrame(main_frame, text="Recording", padding="10")
        record_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.record_button = ttk.Button(record_frame, text="Start Recording", 
                                       command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        self.recording_label = ttk.Label(record_frame, text="Not Recording", 
                                        foreground='red')
        self.recording_label.grid(row=0, column=1)
        
        self.frame_count_label = ttk.Label(record_frame, text="Frames: 0")
        self.frame_count_label.grid(row=0, column=2, padx=(10, 0))
        
        # Macro name entry
        ttk.Label(record_frame, text="Macro Name:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.macro_name_entry = ttk.Entry(record_frame, width=20)
        self.macro_name_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Playback section
        playback_frame = ttk.LabelFrame(main_frame, text="Playback", padding="10")
        playback_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.play_button = ttk.Button(playback_frame, text="Play Macro", 
                                     command=self.play_macro)
        self.play_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(playback_frame, text="Stop", 
                                     command=self.stop_macro, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.loop_var = tk.BooleanVar()
        self.loop_checkbox = ttk.Checkbutton(playback_frame, text="Loop", 
                                           variable=self.loop_var)
        self.loop_checkbox.grid(row=0, column=2)
        
        # Macro list
        macro_frame = ttk.LabelFrame(main_frame, text="Saved Macros", padding="10")
        macro_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        macro_frame.columnconfigure(0, weight=1)
        macro_frame.rowconfigure(0, weight=1)
        
        # Macro listbox with scrollbar
        list_frame = ttk.Frame(macro_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.macro_listbox = tk.Listbox(list_frame, height=8)
        self.macro_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.macro_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.macro_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Macro management buttons
        button_frame = ttk.Frame(macro_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Macro", 
                  command=self.save_current_macro).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Macro", 
                  command=self.delete_selected_macro).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Load Macros", 
                  command=self.load_macros).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="Save All", 
                  command=self.save_all_macros).grid(row=0, column=3)
        
        # Controller input display
        input_frame = ttk.LabelFrame(main_frame, text="Controller Input", padding="10")
        input_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.input_text = tk.Text(input_frame, height=6, width=70, state='disabled')
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(6, weight=1)
        macro_frame.rowconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
    
    def setup_controller_monitoring(self):
        """Setup controller input monitoring."""
        self.monitor_controller()
    
    def monitor_controller(self):
        """Monitor controller input and update display."""
        # Check controller connection status
        if not self.controller.controller_connected:
            self.controller.connect_controller()
        
        if self.controller.controller_connected:
            self.status_label.config(text="Controller: Connected", foreground='green')
            state = self.controller.get_controller_state()
            if state:
                self.update_input_display(state)
                # Update recording if we're recording
                if self.recording:
                    self.recorder.update_recording()
                    # Update frame count display
                    self.frame_count_label.config(text=f"Frames: {len(self.recorder.macro_data)}")
        else:
            self.status_label.config(text="Controller: Not Connected", foreground='red')
        
        # Schedule next update
        self.root.after(50, self.monitor_controller)
    
    def update_input_display(self, state: Dict[str, Any]):
        """Update the controller input display."""
        self.input_text.config(state='normal')
        self.input_text.delete(1.0, tk.END)
        
        # Display active buttons
        active_buttons = [name for name, pressed in state.get('buttons', {}).items() if pressed]
        if active_buttons:
            self.input_text.insert(tk.END, f"Buttons: {', '.join(active_buttons)}\n")
        
        # Display axis values
        axes = state.get('axes', {})
        if any(abs(v) > 0.1 for v in axes.values()):
            axis_info = [f"{name}: {v:.2f}" for name, v in axes.items() if abs(v) > 0.1]
            self.input_text.insert(tk.END, f"Axes: {', '.join(axis_info)}\n")
        
        # Display hat values
        hats = state.get('hats', {})
        if any(hat != (0, 0) for hat in hats.values()):
            hat_info = [f"{name}: {hat}" for name, hat in hats.items() if hat != (0, 0)]
            self.input_text.insert(tk.END, f"Hats: {', '.join(hat_info)}\n")
        
        self.input_text.config(state='disabled')
    
    def toggle_recording(self):
        """Toggle macro recording."""
        if not self.recording:
            if not self.controller.controller_connected:
                messagebox.showerror("Error", "No controller connected!")
                return
            
            self.recording = True
            self.recorder.start_recording()
            self.record_button.config(text="Stop Recording")
            self.recording_label.config(text="Recording...", foreground='green')
            self.frame_count_label.config(text="Frames: 0")
        else:
            self.recording = False
            macro_data = self.recorder.stop_recording()
            self.record_button.config(text="Start Recording")
            self.recording_label.config(text="Not Recording", foreground='red')
            
            if macro_data:
                messagebox.showinfo("Recording Complete", 
                                  f"Recorded {len(macro_data)} input frames")
            else:
                messagebox.showwarning("Warning", "No input was recorded. Make sure you moved the controller or pressed buttons while recording.")
    
    def play_macro(self):
        """Play the selected macro."""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a macro to play")
            return
        
        macro_name = self.macro_listbox.get(selected[0])
        macro = self.editor.get_macro(macro_name)
        
        if macro:
            self.playing = True
            self.play_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            loop = self.loop_var.get()
            success = self.player.play_macro(macro['data'], loop)
            
            if not success:
                messagebox.showerror("Error", "Could not start macro playback")
                self.playing = False
                self.play_button.config(state='normal')
                self.stop_button.config(state='disabled')
    
    def stop_macro(self):
        """Stop macro playback."""
        self.player.stop_playback()
        self.playing = False
        self.play_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def save_current_macro(self):
        """Save the currently recorded macro."""
        if not self.recorder.macro_data:
            messagebox.showwarning("Warning", "No macro data to save. Make sure you recorded something first!")
            return
        
        name = self.macro_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a macro name")
            return
        
        self.editor.create_macro(name, self.recorder.macro_data)
        self.update_macro_list()
        messagebox.showinfo("Success", f"Macro '{name}' saved successfully with {len(self.recorder.macro_data)} frames")
    
    def delete_selected_macro(self):
        """Delete the selected macro."""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a macro to delete")
            return
        
        macro_name = self.macro_listbox.get(selected[0])
        if messagebox.askyesno("Confirm", f"Delete macro '{macro_name}'?"):
            self.editor.delete_macro(macro_name)
            self.update_macro_list()
    
    def load_macros(self):
        """Load macros from file."""
        filename = filedialog.askopenfilename(
            title="Load Macros",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.editor.load_macros(filename)
            self.update_macro_list()
            messagebox.showinfo("Success", "Macros loaded successfully")
    
    def save_all_macros(self):
        """Save all macros to file."""
        if not self.editor.macros:
            messagebox.showwarning("Warning", "No macros to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Macros",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.editor.save_macros(filename)
            messagebox.showinfo("Success", "Macros saved successfully")
    
    def update_macro_list(self):
        """Update the macro list display."""
        self.macro_listbox.delete(0, tk.END)
        for macro_name in self.editor.list_macros():
            self.macro_listbox.insert(tk.END, macro_name)
    
    def show_vigembus_help(self):
        """Show ViGEmBus installation help dialog."""
        help_text = """ViGEmBus Driver Installation Required

To use virtual gamepad input simulation, you need to install the ViGEmBus driver.

Installation Options:

1. AUTOMATIC (Recommended):
   Run: python install_vigembus.py
   
2. MANUAL:
   - Download from: https://github.com/ViGEm/ViGEmBus/releases/latest
   - Run the installer as Administrator
   - Restart your computer

3. ALTERNATIVE:
   - Use keyboard/mouse simulation instead
   - Some emulators may not require virtual gamepad

After installation, restart this application to enable input simulation."""
        
        messagebox.showinfo("ViGEmBus Installation Help", help_text)
    
    def run(self):
        """Run the application."""
        self.update_macro_list()
        self.root.mainloop()

def main():
    """Main entry point."""
    try:
        app = XboxMacroHUD()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
