"""
Global state management for Gesture Control System.
"""

import time
from collections import deque
from threading import Lock
from src.config import CURSOR_HISTORY

# Get screen dimensions from config
from src.config import SCREEN_W, SCREEN_H

# ═══════════════════════════════════════════════════════════
#  CURSOR STATE
# ═══════════════════════════════════════════════════════════
cursor_x        = SCREEN_W / 2
cursor_y        = SCREEN_H / 2
cursor_history  = deque(maxlen=CURSOR_HISTORY)

# ═══════════════════════════════════════════════════════════
#  COOLDOWN TIMERS
# ═══════════════════════════════════════════════════════════
last_click_time  = 0.0
last_app_time    = 0.0
last_volume_time = 0.0
last_media_time  = 0.0

# ═══════════════════════════════════════════════════════════
#  GESTURE TRACKING
# ═══════════════════════════════════════════════════════════
gesture_start    = {}       # gesture_name -> first-seen time

# ═══════════════════════════════════════════════════════════
#  TRANSITION MACHINE (FIST ↔ PALM)
# ═══════════════════════════════════════════════════════════
prev_gesture     = "NONE"
prev_gesture_t   = 0.0
transition_done  = {}       # key -> time fired (prevents re-fire)

# ═══════════════════════════════════════════════════════════
#  HUD STATE
# ═══════════════════════════════════════════════════════════
hud_msg   = ""
hud_msg_t = 0.0

# ═══════════════════════════════════════════════════════════
#  ANIMATION STATE
# ═══════════════════════════════════════════════════════════
scan_y       = 0
frame_count  = 0
fps_display  = 0.0
fps_t0       = time.time()

# ═══════════════════════════════════════════════════════════
#  SCROLL STATE
# ═══════════════════════════════════════════════════════════
scroll_prev_y   = None      # previous TWO-finger midpoint Y (normalised 0-1)
scroll_last_t   = 0.0       # last scroll fire time

# ═══════════════════════════════════════════════════════════
#  MEDIAPIPE LIVE STREAM STATE
# ═══════════════════════════════════════════════════════════
latest_gesture         = "NONE"
latest_lm_list         = None
latest_callback_time   = 0
result_lock            = Lock()

# ═══════════════════════════════════════════════════════════
#  HELPER FUNCTIONS FOR STATE UPDATES
# ═══════════════════════════════════════════════════════════
def reset_scroll():
    """Reset scroll tracking state."""
    global scroll_prev_y
    scroll_prev_y = None

def update_cursor(x, y):
    """Update cursor position and history."""
    global cursor_x, cursor_y
    cursor_x = x
    cursor_y = y
    cursor_history.append((int(x), int(y)))

def flash_message(msg):
    """Display a flash message on HUD."""
    global hud_msg, hud_msg_t
    hud_msg = msg
    hud_msg_t = time.time()

def clear_gesture_start():
    """Clear gesture start times."""
    global gesture_start
    gesture_start.clear()

def get_screen_size():
    """Get current screen dimensions."""
    return SCREEN_W, SCREEN_H
