"""
Gesture dispatch and action handling for Gesture Control System.
"""

import time
import pyautogui
from src.config import (
    SCREEN_W, SCREEN_H, SMOOTH_NORMAL, CLICK_COOLDOWN, APP_COOLDOWN,
    VOLUME_COOLDOWN, GESTURE_HOLD_SEC, THUMB_HOLD_SEC,
    SCROLL_COOLDOWN, SCROLL_DEADZONE, SCROLL_LINES, PREV_GESTURE_WINDOW
)
from src.helpers import (
    lerp, traffic_lerp, confirm_gesture, media_play_pause, volume_up, 
    volume_down, win_maximise, win_minimise, win_quit, open_app
)
import src.state as state

# ═══════════════════════════════════════════════════════════
#  TRANSITION MACHINE  (FIST ↔ PALM)
# ═══════════════════════════════════════════════════════════
def check_transition(current):
    """
    Detects when user transitions from FIST→PALM (maximise) or
    PALM→FIST (quit). The previous gesture is remembered for
    PREV_GESTURE_WINDOW seconds so the user has time to make the
    transition naturally. Each transition fires only once per occurrence.
    """
    now = time.time()

    fired = None
    if current == "PALM" and state.prev_gesture == "FIST":
        key = "F2P"
        if key not in state.transition_done or now - state.transition_done[key] > 2.0:
            if now - state.prev_gesture_t < PREV_GESTURE_WINDOW:
                state.transition_done[key] = now
                fired = "FIST_TO_PALM"

    elif current == "FIST" and state.prev_gesture == "PALM":
        key = "P2F"
        if key not in state.transition_done or now - state.transition_done[key] > 2.0:
            if now - state.prev_gesture_t < PREV_GESTURE_WINDOW:
                state.transition_done[key] = now
                fired = "PALM_TO_FIST"

    # Maintain prev_gesture memory
    if current != state.prev_gesture:
        state.prev_gesture   = current
        state.prev_gesture_t = now

    return fired

# ═══════════════════════════════════════════════════════════
#  DISPATCH ACTIONS
# ═══════════════════════════════════════════════════════════
def dispatch_cursor(lm):
    """Handle cursor movement with index finger."""
    sf = traffic_lerp(state.cursor_x, state.cursor_y)
    state.cursor_x = lerp(state.cursor_x, (1.0 - lm[8].x) * SCREEN_W, sf)
    state.cursor_y = lerp(state.cursor_y, lm[8].y * SCREEN_H, sf)
    pyautogui.moveTo(state.cursor_x, state.cursor_y)
    state.cursor_history.append((int(state.cursor_x), int(state.cursor_y)))
    state.reset_scroll()

def dispatch_scroll(lm, now):
    """Handle scrolling with two fingers."""
    mid_y = (lm[8].y + lm[12].y) / 2.0

    if state.scroll_prev_y is not None:
        delta = mid_y - state.scroll_prev_y
        if abs(delta) > SCROLL_DEADZONE and now - state.scroll_last_t > SCROLL_COOLDOWN:
            if delta < 0:
                pyautogui.scroll(SCROLL_LINES)
                state.flash_message("▲  SCROLL UP")
            else:
                pyautogui.scroll(-SCROLL_LINES)
                state.flash_message("▼  SCROLL DOWN")
            state.scroll_last_t = now

    state.scroll_prev_y = mid_y

def dispatch_pinch(now):
    """Handle pinch gesture (left click)."""
    if now - state.last_click_time > CLICK_COOLDOWN:
        pyautogui.click()
        state.last_click_time = now
        state.flash_message("● LEFT CLICK")
    state.reset_scroll()

def dispatch_three_fingers(now):
    """Handle three-finger gesture (right click)."""
    if now - state.last_click_time > CLICK_COOLDOWN:
        pyautogui.rightClick()
        state.last_click_time = now
        state.flash_message("● RIGHT CLICK")
    state.reset_scroll()

def dispatch_thumb(now):
    """Handle thumb gesture (minimise window)."""
    if confirm_gesture("THUMB", THUMB_HOLD_SEC):
        win_minimise()
        state.flash_message("▼  MINIMISE WINDOW")
        state.gesture_start.clear()
    state.reset_scroll()

def dispatch_fist(now):
    """Handle fist gesture (media play/pause)."""
    if confirm_gesture("FIST") and now - state.last_media_time > APP_COOLDOWN:
        media_play_pause()
        state.last_media_time = now
        state.flash_message("⏯  MEDIA PLAY/PAUSE")
    state.reset_scroll()

def dispatch_palm(now):
    """Handle palm gesture (launch Chrome)."""
    if confirm_gesture("PALM") and now - state.last_app_time > APP_COOLDOWN:
        open_app("Google Chrome")
        state.last_app_time = now
        state.flash_message("⬡  LAUNCH CHROME")
    state.reset_scroll()

def dispatch_idx_ring(now):
    """Handle index+ring gesture (open VS Code)."""
    if confirm_gesture("IDX_RING") and now - state.last_app_time > APP_COOLDOWN:
        open_app("Visual Studio Code")
        state.last_app_time = now
        state.flash_message("⬡  OPEN VS CODE")
    state.reset_scroll()

def dispatch_idx_pinky(now):
    """Handle index+pinky gesture (open Spotify)."""
    if confirm_gesture("IDX_PINKY") and now - state.last_app_time > APP_COOLDOWN:
        open_app("Spotify")
        state.last_app_time = now
        state.flash_message("⬡  OPEN SPOTIFY")
    state.reset_scroll()

def dispatch_middle(now):
    """Handle middle finger gesture (volume down)."""
    if now - state.last_volume_time > VOLUME_COOLDOWN:
        volume_down()
        state.last_volume_time = now
    state.reset_scroll()

def dispatch_pinky(now):
    """Handle pinky gesture (volume up)."""
    if now - state.last_volume_time > VOLUME_COOLDOWN:
        volume_up()
        state.last_volume_time = now
    state.reset_scroll()

# ═══════════════════════════════════════════════════════════
#  MAIN DISPATCH
# ═══════════════════════════════════════════════════════════
def dispatch(gesture, lm):
    """
    Main gesture dispatch function. Routes gestures to appropriate handlers.
    """
    now = time.time()

    # ── transition check: FIST<->PALM ───────────────────────
    transition = check_transition(gesture)
    if transition == "FIST_TO_PALM":
        win_maximise()
        state.flash_message("⬜  WINDOW MAXIMISED")
        return
    if transition == "PALM_TO_FIST":
        win_quit()
        state.flash_message("✕  QUIT APP  (Cmd+Q)")
        return

    # ── route to appropriate handler ──────────────────────────
    if gesture == "POINT":
        dispatch_cursor(lm)
    elif gesture == "TWO":
        dispatch_scroll(lm, now)
    elif gesture == "PINCH":
        dispatch_pinch(now)
    elif gesture == "THREE":
        dispatch_three_fingers(now)
    elif gesture == "THUMB":
        dispatch_thumb(now)
    elif gesture == "FIST":
        dispatch_fist(now)
    elif gesture == "PALM":
        dispatch_palm(now)
    elif gesture == "IDX_RING":
        dispatch_idx_ring(now)
    elif gesture == "IDX_PINKY":
        dispatch_idx_pinky(now)
    elif gesture == "MIDDLE":
        dispatch_middle(now)
    elif gesture == "PINKY":
        dispatch_pinky(now)
    else:
        state.reset_scroll()
