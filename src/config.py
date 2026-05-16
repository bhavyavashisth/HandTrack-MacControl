"""
Configuration constants for Gesture Control System.
"""

import pyautogui

# Get screen dimensions
SCREEN_W, SCREEN_H = pyautogui.size()

# ═══════════════════════════════════════════════════════════
#  CAMERA & DISPLAY
# ═══════════════════════════════════════════════════════════
CAM_W, CAM_H        = 640, 480
WIN_W, WIN_H        = 960, 640

# ═══════════════════════════════════════════════════════════
#  CURSOR SMOOTHING
# ═══════════════════════════════════════════════════════════
SMOOTH_NORMAL       = 0.18      # default cursor lerp factor
SMOOTH_SLOW         = 0.05      # lerp when deep inside traffic-light zone
CURSOR_HISTORY      = 8

# ═══════════════════════════════════════════════════════════
#  GESTURE TIMING
# ═══════════════════════════════════════════════════════════
GESTURE_HOLD_SEC    = 0.80      # hold for FIST/PALM media+chrome
DBLCLICK_HOLD_SEC   = 0.60      # hold TWO for double-click
THUMB_HOLD_SEC      = 0.50      # hold THUMB for minimise
CLICK_COOLDOWN      = 0.35
APP_COOLDOWN        = 2.0
VOLUME_COOLDOWN     = 0.10

# ═══════════════════════════════════════════════════════════
#  TRAFFIC-LIGHT ZONE (macOS buttons)
# ═══════════════════════════════════════════════════════════
# Located at top-left where close/minimise/maximise buttons are
TRAFFIC_ZONE_X      = 120
TRAFFIC_ZONE_Y      = 45

# ═══════════════════════════════════════════════════════════
#  TRANSITIONS
# ═══════════════════════════════════════════════════════════
PREV_GESTURE_WINDOW = 0.70      # how long previous gesture is remembered

# ═══════════════════════════════════════════════════════════
#  SCROLLING
# ═══════════════════════════════════════════════════════════
SCROLL_COOLDOWN = 0.07      # seconds between scroll ticks
SCROLL_DEADZONE = 0.007     # minimum normalised Y delta
SCROLL_LINES    = 4         # scroll lines per tick

# ═══════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════
HUD_DUR         = 1.4       # flash message duration
SCAN_SPEED      = 2         # scanline animation speed

# ═══════════════════════════════════════════════════════════
#  COLORS
# ═══════════════════════════════════════════════════════════
C_CYAN    = (0, 255, 220)
C_MAGENTA = (255, 0, 180)
C_YELLOW  = (0, 230, 255)
C_GREEN   = (0, 255, 120)
C_ORANGE  = (30, 160, 255)
C_WHITE   = (220, 220, 220)
C_DIM     = (80, 80, 80)
C_BG      = (10, 12, 18)

# ═══════════════════════════════════════════════════════════
#  HAND LANDMARKS
# ═══════════════════════════════════════════════════════════
TIP = [4, 8, 12, 16, 20]    # finger tip indices
PIP = [3, 7, 11, 15, 19]    # proximal interphalangeal indices

# ═══════════════════════════════════════════════════════════
#  GESTURE LABELS
# ═══════════════════════════════════════════════════════════
SHORT_LABELS = {
    "POINT"    : "CURSOR MOVE",
    "PINCH"    : "LEFT CLICK",
    "THREE"    : "RIGHT CLICK",
    "TWO"      : "SCROLL  ▲ up  ▼ down",
    "FIST"     : "FIST  [→ palm: MAXIMISE]",
    "PALM"     : "PALM  [→ fist: QUIT APP]",
    "THUMB"    : "MINIMISE (hold)",
    "MIDDLE"   : "VOLUME DOWN",
    "PINKY"    : "VOLUME UP",
    "IDX_RING" : "OPEN VS CODE (hold)",
    "IDX_PINKY": "OPEN SPOTIFY (hold)",
    "UNKNOWN"  : "—",
    "NONE"     : "—",
}

HOLD_SECS = {
    "FIST"     : GESTURE_HOLD_SEC,
    "PALM"     : GESTURE_HOLD_SEC,
    "THUMB"    : THUMB_HOLD_SEC,
    "IDX_RING" : GESTURE_HOLD_SEC,
    "IDX_PINKY": GESTURE_HOLD_SEC,
}
