# Gesture Control System - Modular Architecture

This refactored version of the Gesture Control System has been split into smaller, maintainable modules with improved organization and readability.

## Project Structure

```
HandTrack-MacControl/
├── main.py                 # Entry point - runs the application
├── config.py              # All configuration constants and settings
├── state.py               # Global state management
├── helpers.py             # Utility functions (math, system, control)
├── gesture.py             # Gesture classification logic
├── hud.py                 # HUD rendering functions
├── dispatch.py            # Gesture dispatch and action handling
├── test_imports.py        # Module import testing
├── hand_landmarker.task   # MediaPipe hand detection model
├── gesture_env/           # Python virtual environment
├── requirements.txt       # Project dependencies
└── README.md             # Original documentation
```

## Module Descriptions

### `config.py` - Configuration & Constants
**Purpose:** Centralized configuration management

**Contains:**
- Screen dimensions and camera settings
- Cursor smoothing parameters
- Gesture timing thresholds
- Color palette (cyberpunk theme)
- Hand landmark indices (TIP, PIP)
- Gesture labels and hold durations
- Traffic-light zone boundaries

**Key exports:**
- `CAM_W, CAM_H` - Camera resolution
- `SMOOTH_NORMAL, SMOOTH_SLOW` - Lerp factors
- `GESTURE_HOLD_SEC`, `THUMB_HOLD_SEC` - Timing constants
- `C_CYAN, C_MAGENTA, C_YELLOW...` - Color definitions
- `HOLD_SECS` - Gesture hold requirements

---

### `state.py` - Global State Management
**Purpose:** Manages all mutable application state with thread-safe access

**Contains:**
- Cursor position and history tracking
- Cooldown timers (click, app, volume, media)
- Gesture start times for hold detection
- Transition machine state (FIST ↔ PALM)
- HUD message and animation state
- Scroll tracking state
- MediaPipe live stream state (thread-locked)
- FPS calculation state

**Key exports:**
- `cursor_x, cursor_y` - Current cursor position
- `gesture_start` - Dict tracking gesture hold times
- `result_lock` - Threading lock for MediaPipe callbacks
- `reset_scroll()` - Clear scroll tracking
- `flash_message()` - Display HUD message
- `clear_gesture_start()` - Reset gesture timers

---

### `helpers.py` - Utility Functions
**Purpose:** Reusable helper functions for math, system calls, and window/media control

**Contains:**
- **Math helpers:**
  - `dist(a, b)` - Euclidean distance
  - `lerp(a, b, t)` - Linear interpolation
  - `traffic_lerp()` - Smart lerp for traffic-light zone proximity

- **System helpers:**
  - `open_app(name)` - Launch macOS applications
  - `run_apple(script)` - Execute AppleScript

- **Media control:**
  - `media_play_pause()` - Toggle media playback
  - `volume_up() / volume_down()` - Adjust system volume

- **Window management:**
  - `win_maximise()` - Maximize window (Ctrl+Cmd+F)
  - `win_minimise()` - Minimize window (Cmd+M)
  - `win_quit()` - Close application (Cmd+Q)

- **Gesture helpers:**
  - `confirm_gesture()` - Check if gesture held long enough
  - `hold_pct()` - Get hold progress percentage (0-1)

---

### `gesture.py` - Gesture Classification
**Purpose:** Hand landmark analysis and gesture recognition

**Contains:**
- `finger_states(lm)` - Determine which fingers are extended
- `classify_gesture(lm)` - Classify hand gesture from landmarks

**Recognized gestures:**
- `POINT` - Index finger extended (cursor move)
- `PINCH` - Thumb + index touching (left click)
- `THREE` - Three fingers extended (right click)
- `TWO` - Two fingers extended (scroll)
- `FIST` - All fingers closed (media control)
- `PALM` - All fingers extended (app launcher)
- `THUMB` - Thumb only (minimise)
- `MIDDLE` - Middle finger (volume down)
- `PINKY` - Pinky finger (volume up)
- `IDX_RING` - Index + ring (VS Code)
- `IDX_PINKY` - Index + pinky (Spotify)
- `UNKNOWN` - Unrecognized configuration

---

### `hud.py` - HUD Rendering
**Purpose:** All visual display and rendering functions

**Contains:**
- `draw_scanlines()` - Cyberpunk scanline effect
- `draw_scan_beam()` - Animated scanning beam
- `draw_border_and_corners()` - HUD frame with corners
- `draw_precision_badge()` - Traffic-light zone indicator
- `draw_hand_landmarks()` - Hand skeleton visualization
- `draw_gesture_label()` - Current gesture display
- `draw_flash_message()` - Fading notification text
- `draw_hold_progress()` - Progress bar for hold gestures
- `draw_transition_hints()` - Helpful gesture hints
- `draw_top_info()` - FPS, gesture, cursor position display
- `draw_cursor_trail()` - Movement history line
- `draw_hud()` - Main rendering orchestrator

**Key feature:**
- All rendering uses `state` module for current values
- Modular design allows easy customization of individual UI elements
- Color scheme imported from `config`

---

### `dispatch.py` - Gesture Dispatch & Actions
**Purpose:** Routes recognized gestures to appropriate action handlers

**Transition Machine:**
- `check_transition()` - FIST→PALM (maximize) and PALM→FIST (quit) detection

**Dispatch handlers:**
- `dispatch_cursor()` - Move cursor with precision mode
- `dispatch_scroll()` - Vertical scroll with index+middle
- `dispatch_pinch()` - Left click
- `dispatch_three_fingers()` - Right click
- `dispatch_thumb()` - Minimize window
- `dispatch_fist()` - Media play/pause
- `dispatch_palm()` - Launch Chrome
- `dispatch_idx_ring()` - Open VS Code
- `dispatch_idx_pinky()` - Open Spotify
- `dispatch_middle()` - Volume down
- `dispatch_pinky()` - Volume up
- `dispatch()` - Main router that coordinates all actions

**Features:**
- Cooldown management to prevent rapid-fire actions
- Gesture hold confirmation
- Transition detection with memory window
- Scroll deadzone and rate limiting
- Flash message notifications

---

### `main.py` - Application Entry Point
**Purpose:** Initializes and runs the gesture control system

**Key sections:**
- Configuration and setup (camera, window, MediaPipe)
- Main event loop (frame capture, processing, dispatch)
- MediaPipe callback `on_live_result()`
- Legend printing
- Error handling and graceful shutdown

**Flow:**
1. Initialize camera (640×480 @ 60 FPS)
2. Create OpenCV window and MediaPipe hand detector
3. Loop: capture frame → detect hand → classify gesture → dispatch actions → render HUD
4. Handle exit (Q key or Ctrl+C)

---

## Usage

### Run the application:
```bash
python main.py
```

Or using the virtual environment:
```bash
./gesture_env/Scripts/python main.py
```

### Test all modules:
```bash
./gesture_env/Scripts/python test_imports.py
```

---

## Gesture Guide

### Cursor & Clicks
- **☝ Point (1 finger)** → Move cursor (slows near traffic-light buttons)
- **🤏 Pinch** → Left click
- **3️⃣ Three fingers** → Right click

### Scrolling
- **✌ Two fingers ↑** → Scroll up
- **✌ Two fingers ↓** → Scroll down

### Window Management
- **✊→🖐 Fist→Palm** → Maximize window
- **🖐→✊ Palm→Fist** → Quit application
- **👍 Thumb (hold)** → Minimize window

### Media & Apps
- **✊ Fist (hold 0.8s)** → Media play/pause
- **🖐 Palm (hold 0.8s)** → Launch Chrome
- **🤘 Index+Ring (hold)** → Open VS Code
- **🤙 Index+Pinky (hold)** → Open Spotify

### Volume
- **🖕 Middle finger** → Volume down
- **🤙 Pinky only** → Volume up

---

## Configuration

All constants are in `config.py`. Common adjustments:

```python
# Cursor smoothing
SMOOTH_NORMAL = 0.18    # Normal smoothness
SMOOTH_SLOW = 0.05      # Near traffic-light zone

# Gesture timing
GESTURE_HOLD_SEC = 0.80     # Hold duration for media/app gestures
THUMB_HOLD_SEC = 0.50       # Hold duration for minimize
CLICK_COOLDOWN = 0.35       # Minimum time between clicks

# Traffic-light zone (where macOS buttons are)
TRAFFIC_ZONE_X = 120
TRAFFIC_ZONE_Y = 45

# Scrolling
SCROLL_LINES = 4            # Lines per scroll tick
SCROLL_COOLDOWN = 0.07      # Minimum time between scrolls
SCROLL_DEADZONE = 0.007     # Minimum hand movement to trigger scroll
```

---

## Benefits of Modular Architecture

✅ **Improved Readability** - Each module has a single, clear responsibility
✅ **Easier Maintenance** - Bug fixes and updates are localized to relevant modules
✅ **Better Testing** - Modules can be tested independently
✅ **Code Reusability** - Utilities and helpers can be imported by other projects
✅ **Scalability** - Easy to add new gestures or features
✅ **Documentation** - Clear module separation makes code self-documenting
✅ **Collaboration** - Team members can work on different modules in parallel

---

## Dependencies

```
opencv-python
mediapipe
pyautogui
numpy
```

Install via:
```bash
pip install -r requirements.txt
```

---

## Platform Support

🍎 **Optimized for macOS** (Intel 2019+)

⚠️ **Limited support for Windows/Linux** (no AppleScript, some shortcuts unavailable)

---

## License

Original code - See repository README.md

Refactoring - Modular architecture improvements (2026)
