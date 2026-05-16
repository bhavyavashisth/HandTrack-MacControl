# Module Dependencies & Import Graph

## Dependency Chart

```
main.py
├── config.py
├── state.py (imports: config)
├── gesture.py (imports: config, helpers)
├── hud.py (imports: config, helpers, state, gesture)
├── dispatch.py (imports: config, helpers, state)
└── cv2, mediapipe, numpy, pyautogui

config.py
└── pyautogui

state.py
├── config.py
└── threading, time, collections

helpers.py
├── config.py
├── state.py
├── math, subprocess, pyautogui, time

gesture.py
├── config.py
├── helpers.py

hud.py
├── config.py
├── helpers.py
├── state.py
├── cv2, mediapipe, time

dispatch.py
├── config.py
├── helpers.py
├── state.py
└── pyautogui, time
```

## Import Order (Dependency Resolution)

When importing modules, follow this order to avoid circular dependencies:

1. **config.py** - No dependencies (except pyautogui for screen size)
2. **state.py** - Imports config
3. **helpers.py** - Imports config, state
4. **gesture.py** - Imports config, helpers
5. **hud.py** - Imports config, helpers, state, gesture
6. **dispatch.py** - Imports config, helpers, state
7. **main.py** - Imports all above modules

## Circular Dependency: AVOIDED ✓

The refactored code avoids circular imports by:
- `helpers.py` and `dispatch.py` import `state`, but `state` only imports `config`
- Late imports are used where necessary (e.g., in `dispatch.py`: `from config import GESTURE_HOLD_SEC`)
- All global state lives in `state.py` only

## Module Interaction Flow

```
main.py (entry point)
│
├─→ MediaPipe detects hand
│   └─→ on_live_result() callback
│       └─→ gesture.classify_gesture() in state
│
├─→ dispatch(gesture, lm)
│   ├─→ check_transition() 
│   ├─→ dispatch_<gesture>()
│   │   └─→ helpers (media, window, volume, etc.)
│   └─→ state (cursor, cooldowns, messages)
│
└─→ draw_hud()
    ├─→ hud rendering functions
    ├─→ reads from state (cursor, gesture, etc.)
    └─→ uses config (colors, labels, etc.)
```

## Adding New Features

### Add a new gesture:
1. Update `config.py` - Add to `SHORT_LABELS` and gesture constants
2. Update `gesture.py` - Add classification logic to `classify_gesture()`
3. Update `dispatch.py` - Add `dispatch_<gesture>()` function
4. Update `main.py` or `dispatch.py` - Route the gesture to handler

### Add a new system call:
1. Add function to `helpers.py`
2. Use it in appropriate `dispatch_<gesture>()` handler

### Add new state variable:
1. Declare in `state.py`
2. Use helper functions (`update_cursor()`, `flash_message()`, etc.) to modify
3. Import state in modules that need it

### Customize HUD rendering:
1. Modify functions in `hud.py`
2. Colors are in `config.py` (C_CYAN, C_MAGENTA, etc.)
3. Font settings in individual `draw_*()` functions

---

## Testing Single Modules

```python
# Test gesture classification
from gesture import classify_gesture
from config import TIP, PIP

# Mock landmarks and test
gesture = classify_gesture(landmarks)
print(f"Detected: {gesture}")
```

```python
# Test helpers
from helpers import dist, lerp, traffic_lerp

d = dist(point_a, point_b)
smooth = traffic_lerp(cursor_x, cursor_y)
```

```python
# Test state
import state
state.flash_message("Test message")
state.update_cursor(100, 200)
```

---

## Performance Considerations

- **state.py**: Uses locks for thread-safe access (MediaPipe callback)
- **gesture.py**: Light computation (distance checks, comparisons)
- **hud.py**: OpenCV operations on 960×640 display
- **dispatch.py**: Action dispatch is instant with cooldown management

## Memory Usage

- ~50 MB base (OpenCV, MediaPipe)
- ~8 KB state (cursor history limited to 8 points)
- Negligible per-frame overhead
