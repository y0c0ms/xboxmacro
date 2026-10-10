# Xbox Controller Macro HUD

A Tkinter HUD for recording, saving, and replaying Xbox controller macros through a virtual gamepad, or through keyboard/mouse as a fallback.

## Features

- **Controller detection**: Connects to the first joystick reported by pygame
- **Live input display**: Shows current button, axis, and D-pad state
- **Macro recording**: Stores a snapshot of every controller state read while recording, with relative timestamps
- **Macro playback**: Replays a saved macro, optionally looping
- **Virtual gamepad output**: Injects an Xbox 360 controller through ViGEmBus (vgamepad)
- **Keyboard/mouse fallback**: If ViGEmBus is unavailable, maps buttons and D-pad to keys and sticks to mouse movement
- **Macro library**: Save, delete, load, and export macros as JSON

## Run it

```bash
pip install -r requirements.txt
python xbox_macro_hud.py
```

Or install the dependencies with the helper script and launch through the launcher:

```bash
python install_dependencies.py
python run_macro_hud.py
```

`run_macro_hud.py` expects `xbox_macro_hud.py` and `requirements.txt` in the current directory, so run it from the repository root.

## Requirements

- Python with `pygame`, `vgamepad`, and `pynput` (see `requirements.txt`)
- An Xbox controller (wired or wireless) connected before the app starts
- ViGEmBus driver for virtual gamepad output (Windows). Without it, the app uses the keyboard/mouse fallback.

### Windows notes

- If `vgamepad` fails to load, install the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) and retry.
- ViGEmBus can be installed with `python install_vigembus.py`, or manually from the [ViGEmBus releases page](https://github.com/ViGEm/ViGEmBus/releases/latest) (run the installer as Administrator, then restart).

## Usage

1. Connect your Xbox controller.
2. Start the app with `python xbox_macro_hud.py`. The status labels show whether the controller and input simulation are available.

### Recording

1. Enter a name in **Macro Name**.
2. Click **Start Recording**, perform the inputs, then click **Stop Recording**.
3. Click **Save Macro**. Saving under an existing name overwrites that macro.

### Playback

1. Select a macro in **Saved Macros**.
2. Tick **Loop** to repeat it continuously.
3. Click **Play Macro**, and **Stop** to halt it.

### Managing macros

- **Save All**: Export every macro to a JSON file
- **Load Macros**: Replace the current list with macros from a JSON file
- **Delete Macro**: Remove the selected macro (asks for confirmation)

## Controller inputs

- **Buttons**: A, B, X, Y, LB, RB, Back, Start, Left Stick, Right Stick
- **Sticks and triggers**: Recorded as pygame axes
- **D-pad**: Recorded as a hat

### Keyboard/mouse fallback mapping

| Controller | Key |
|---|---|
| A / B / X / Y | `a` / `b` / `x` / `y` |
| LB / RB | `q` / `e` |
| Back / Start | `Escape` / `Enter` |
| Left Stick / Right Stick | `Space` / `Shift` |
| D-pad | Arrow keys |

Stick movement is simulated as mouse movement.

## File format

Macros are saved as JSON keyed by name:

```json
{
  "macro_name": {
    "name": "macro_name",
    "data": [
      {
        "buttons": {"button_0": true, "button_1": false},
        "axes": {"axis_0": 0.5, "axis_1": -0.3},
        "hats": {"hat_0": [0, 1]},
        "timestamp": 1234567890.123,
        "relative_time": 0.0
      }
    ],
    "created": "2024-01-01T12:00:00",
    "modified": "2024-01-01T12:00:00"
  }
}
```

## Troubleshooting

### Controller not detected
- Connect the controller before starting the app.
- Check that pygame sees it:
  ```python
  import pygame
  pygame.init()
  pygame.joystick.init()
  print(f"Controllers found: {pygame.joystick.get_count()}")
  ```

### Recording issues
- Connect the controller before clicking **Start Recording**.
- Press buttons or move sticks while recording. A recording with no input shows a warning.
- Enter a macro name before saving.

### Playback issues
- If the virtual gamepad does not appear to work, check the **Input Simulation** status label. A ViGEmBus error means the driver is missing or was not restarted after install.
- Without ViGEmBus, playback goes to the keyboard/mouse fallback, so the target application must accept those inputs.

## Limitations

- Virtual gamepad output depends on the Windows ViGEmBus driver.
- The keyboard/mouse fallback is a coarse approximation of controller input.
- Some systems may require administrator privileges for input simulation.

## Future enhancements

- Macro timing adjustment tools
- Visual macro editor with timeline
- Support for multiple controller profiles
- Advanced macro conditions and triggers

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and personal use only. Please respect the terms of service of any games or applications you use this tool with. The authors are not responsible for any misuse of this software.
