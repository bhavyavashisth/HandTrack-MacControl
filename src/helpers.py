"""
Helper functions for Gesture Control System.
"""

import math
import os
import sys
import subprocess
import pyautogui
import time
from src.config import TRAFFIC_ZONE_X, TRAFFIC_ZONE_Y, SMOOTH_NORMAL, SMOOTH_SLOW
import src.state as state

# ═══════════════════════════════════════════════════════════
#  MATH HELPERS
# ═══════════════════════════════════════════════════════════
def dist(a, b):
    """Calculate Euclidean distance between two points."""
    return math.hypot(a.x - b.x, a.y - b.y)

def lerp(a, b, t):
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t

def traffic_lerp(cx, cy):
    """
    Returns smooth lerp factor based on proximity to traffic-light zone.
    Decreases smoothly from SMOOTH_NORMAL to SMOOTH_SLOW as the cursor
    enters the top-left traffic-light zone (macOS buttons area).
    """
    if cx >= TRAFFIC_ZONE_X or cy >= TRAFFIC_ZONE_Y:
        return SMOOTH_NORMAL
    # 0 = deep inside zone, 1 = just at the boundary
    t = min(cx / TRAFFIC_ZONE_X, cy / TRAFFIC_ZONE_Y)
    return lerp(SMOOTH_SLOW, SMOOTH_NORMAL, t)

# ═══════════════════════════════════════════════════════════
#  SYSTEM HELPERS
# ═══════════════════════════════════════════════════════════
WINDOWS_APP_ALIASES = {
    "Google Chrome": "chrome",
    "Visual Studio Code": "code",
    "Spotify": "spotify",
}

def open_app(name):
    """Open an application by name."""
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-a", name],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif sys.platform.startswith("win"):
        cmd = WINDOWS_APP_ALIASES.get(name, name)
        safe_cmd = cmd.replace('"', '\\"')
        subprocess.Popen(f'start "" "{safe_cmd}"', shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        raise NotImplementedError("open_app is only supported on macOS and Windows")

def run_apple(script):
    """Execute an AppleScript command on macOS."""
    if sys.platform != "darwin":
        raise RuntimeError("AppleScript is only supported on macOS")
    subprocess.Popen(["osascript", "-e", script],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ═══════════════════════════════════════════════════════════
#  MEDIA CONTROL
# ═══════════════════════════════════════════════════════════
def media_play_pause():
    """Trigger media play/pause."""
    if sys.platform == "darwin":
        run_apple('tell application "System Events" to key code 100 using {}')
    elif sys.platform.startswith("win"):
        pyautogui.press("playpause")
    else:
        raise NotImplementedError("media_play_pause is only supported on macOS and Windows")

def volume_up():
    """Increase system volume."""
    if sys.platform == "darwin":
        run_apple("set volume output volume (output volume of (get volume settings) + 6)")
    elif sys.platform.startswith("win"):
        pyautogui.press("volumeup")
    else:
        raise NotImplementedError("volume_up is only supported on macOS and Windows")

def volume_down():
    """Decrease system volume."""
    if sys.platform == "darwin":
        run_apple("set volume output volume (output volume of (get volume settings) - 6)")
    elif sys.platform.startswith("win"):
        pyautogui.press("volumedown")
    else:
        raise NotImplementedError("volume_down is only supported on macOS and Windows")

# ═══════════════════════════════════════════════════════════
#  WINDOW MANAGEMENT
# ═══════════════════════════════════════════════════════════
def win_maximise():
    """Maximise current window."""
    if sys.platform == "darwin":
        pyautogui.hotkey("ctrl", "command", "f")
    elif sys.platform.startswith("win"):
        pyautogui.hotkey("win", "up")
    else:
        raise NotImplementedError("win_maximise is only supported on macOS and Windows")

def win_minimise():
    """Minimise current window."""
    if sys.platform == "darwin":
        pyautogui.hotkey("command", "m")
    elif sys.platform.startswith("win"):
        pyautogui.hotkey("win", "down")
        pyautogui.hotkey("win", "down")
    else:
        raise NotImplementedError("win_minimise is only supported on macOS and Windows")

def win_quit():
    """Quit current application."""
    if sys.platform == "darwin":
        pyautogui.hotkey("command", "q")
    elif sys.platform.startswith("win"):
        pyautogui.hotkey("alt", "f4")
    else:
        raise NotImplementedError("win_quit is only supported on macOS and Windows")

# ═══════════════════════════════════════════════════════════
#  GESTURE HOLD CONFIRMATION
# ═══════════════════════════════════════════════════════════
def confirm_gesture(name, hold_sec=None):
    """
    Check if a gesture has been held long enough.
    Returns True if gesture is held for the required duration.
    """
    if hold_sec is None:
        from src.config import GESTURE_HOLD_SEC
        hold_sec = GESTURE_HOLD_SEC
    
    now = time.time()
    if name not in state.gesture_start:
        state.gesture_start[name] = now
        return False
    return (time.time() - state.gesture_start[name]) >= hold_sec

def hold_pct(name, hold_sec):
    """Get the percentage of hold time completed (0.0 to 1.0)."""
    if name not in state.gesture_start:
        return 0.0
    return min((time.time() - state.gesture_start[name]) / hold_sec, 1.0)
