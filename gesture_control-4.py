#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║          GESTURE CONTROL SYSTEM — CYBERPUNK HUD v3              ║
║          Optimized for Intel Mac 2019 · macOS                   ║
╠══════════════════════════════════════════════════════════════════╣
║  CURSOR                                                          ║
║    ☝  1 finger (index)      →  Move cursor                      ║
║                                 (auto precision near ●●● btns)  ║
║  CLICKS                                                          ║
║    🤏  Pinch                 →  Left click                       ║
║    3️⃣  3 fingers             →  Right click                      ║
║    ✌  2 fingers (hold)      →  Double-click                     ║
║  WINDOW MANAGEMENT                                               ║
║    ✊→🖐  Fist then Palm     →  Maximise  (Ctrl+Cmd+F)          ║
║    🖐→✊  Palm then Fist     →  Quit app  (Cmd+Q)               ║
║    👍  Thumb only            →  Minimise  (Cmd+M)               ║
║  MEDIA / SYSTEM                                                  ║
║    ✊  Fist (hold 0.8s)      →  Media Play/Pause                 ║
║    🖐  Palm (hold 0.8s)      →  Launch Chrome                   ║
║    🤘  Index+Ring            →  Open VS Code                    ║
║    🤙  Index+Pinky           →  Open Spotify                    ║
║    🖕  Middle finger only    →  Volume down                      ║
║    🤙  Pinky only            →  Volume up                       ║
╠══════════════════════════════════════════════════════════════════╣
║  INSTALL:  pip install opencv-python mediapipe pyautogui numpy  ║
║  RUN:      python3 gesture_control.py                           ║
║  QUIT:     Press  Q  in the HUD window                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import subprocess
import time
import math
import platform
import sys
from collections import deque

if platform.system() != "Darwin":
    print("[WARN] Designed for macOS. Some features may not work on other OS.")

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
CAM_W, CAM_H        = 640, 480
WIN_W, WIN_H        = 960, 640
SMOOTH_NORMAL       = 0.18      # default cursor lerp factor
SMOOTH_SLOW         = 0.05      # lerp when deep inside traffic-light zone
CURSOR_HISTORY      = 8
GESTURE_HOLD_SEC    = 0.80      # hold for FIST/PALM media+chrome
DBLCLICK_HOLD_SEC   = 0.60      # hold TWO for double-click
THUMB_HOLD_SEC      = 0.50      # hold THUMB for minimise
CLICK_COOLDOWN      = 0.35
APP_COOLDOWN        = 2.0
VOLUME_COOLDOWN     = 0.10
SCAN_SPEED          = 2

# Traffic-light zone: macOS close/minimise/maximise buttons
# They live at the very top-left of every window.
# We use a screen-level proximity region: x < 120, y < 45.
TRAFFIC_ZONE_X      = 120
TRAFFIC_ZONE_Y      = 45

# How long the "previous gesture" memory lasts for FIST<->PALM transitions
PREV_GESTURE_WINDOW = 0.70

SCREEN_W, SCREEN_H  = pyautogui.size()

# ── palette ─────────────────────────────────────────────────
C_CYAN    = (0, 255, 220)
C_MAGENTA = (255, 0, 180)
C_YELLOW  = (0, 230, 255)
C_GREEN   = (0, 255, 120)
C_ORANGE  = (30, 160, 255)
C_WHITE   = (220, 220, 220)
C_DIM     = (80, 80, 80)
C_BG      = (10, 12, 18)

# ═══════════════════════════════════════════════════════════
#  MEDIAPIPE
# ═══════════════════════════════════════════════════════════
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)

# ═══════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════
cursor_x        = SCREEN_W / 2
cursor_y        = SCREEN_H / 2
cursor_history  = deque(maxlen=CURSOR_HISTORY)

last_click_time  = 0.0
last_app_time    = 0.0
last_volume_time = 0.0
last_media_time  = 0.0

gesture_start    = {}   # gesture_name -> first-seen time

scan_y       = 0
frame_count  = 0
fps_display  = 0.0
fps_t0       = time.time()

# transition machine
prev_gesture     = "NONE"
prev_gesture_t   = 0.0
transition_done  = {}       # key -> time fired (prevents re-fire)

# HUD flash message
hud_msg   = ""
hud_msg_t = 0.0
HUD_DUR   = 1.4

# ── scroll state ─────────────────────────────────────────────
scroll_prev_y   = None   # previous TWO-finger midpoint Y (normalised 0-1)
scroll_last_t   = 0.0    # last scroll fire time
SCROLL_COOLDOWN = 0.07   # seconds between scroll ticks
SCROLL_DEADZONE = 0.007  # minimum normalised Y delta to trigger a tick
SCROLL_LINES    = 4      # scroll lines per tick

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
TIP = [4, 8, 12, 16, 20]
PIP = [3, 7, 11, 15, 19]

def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def lerp(a, b, t):
    return a + (b - a) * t

def open_app(name):
    subprocess.Popen(["open", "-a", name],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_apple(script):
    subprocess.Popen(["osascript", "-e", script],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def media_play_pause():
    run_apple('tell application "System Events" to key code 100 using {}')

def volume_up():
    run_apple("set volume output volume (output volume of (get volume settings) + 6)")

def volume_down():
    run_apple("set volume output volume (output volume of (get volume settings) - 6)")

def win_maximise():
    pyautogui.hotkey("ctrl", "command", "f")

def win_minimise():
    pyautogui.hotkey("command", "m")

def win_quit():
    pyautogui.hotkey("command", "q")

def flash(msg):
    global hud_msg, hud_msg_t
    hud_msg   = msg
    hud_msg_t = time.time()

def traffic_lerp(cx, cy):
    """
    Returns smooth lerp factor.
    Decreases smoothly from SMOOTH_NORMAL to SMOOTH_SLOW as the cursor
    enters the top-left traffic-light zone.  The blend is proportional
    to how deep inside the zone the cursor is — no hard snap.
    """
    if cx >= TRAFFIC_ZONE_X or cy >= TRAFFIC_ZONE_Y:
        return SMOOTH_NORMAL
    # 0 = deep inside zone, 1 = just at the boundary
    t = min(cx / TRAFFIC_ZONE_X, cy / TRAFFIC_ZONE_Y)
    return lerp(SMOOTH_SLOW, SMOOTH_NORMAL, t)

# ═══════════════════════════════════════════════════════════
#  GESTURE CLASSIFIER
# ═══════════════════════════════════════════════════════════
def finger_states(lm):
    up = [lm[4].x < lm[3].x]   # thumb
    for i in range(1, 5):
        up.append(lm[TIP[i]].y < lm[PIP[i]].y)
    return up

def classify_gesture(lm):
    up = finger_states(lm)
    n  = sum(up)
    thumb, index, middle, ring, pinky = up

    # pinch beats everything
    if dist(lm[4], lm[8]) < 0.06:
        return "PINCH"

    if n == 0:                                              return "FIST"
    if n == 5:                                              return "PALM"
    if thumb  and not index and not middle and not ring and not pinky: return "THUMB"
    if index  and not middle and not ring  and not pinky:              return "POINT"
    if not index and middle and not ring   and not pinky:              return "MIDDLE"
    if not index and not middle and not ring and pinky:                return "PINKY"
    if index  and middle and not ring and not pinky:                   return "TWO"
    if index  and middle and ring and not pinky:                       return "THREE"
    if index  and not middle and ring and not pinky:                   return "IDX_RING"
    if index  and not middle and not ring and pinky:                   return "IDX_PINKY"
    return "UNKNOWN"

# ═══════════════════════════════════════════════════════════
#  HUD LABELS
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

# ═══════════════════════════════════════════════════════════
#  HOLD HELPERS
# ═══════════════════════════════════════════════════════════
def confirm_gesture(name, hold_sec=None):
    global gesture_start
    if hold_sec is None:
        hold_sec = GESTURE_HOLD_SEC
    now = time.time()
    if name not in gesture_start:
        gesture_start = {name: now}
        return False
    return (time.time() - gesture_start[name]) >= hold_sec

def hold_pct(name, hold_sec):
    if name not in gesture_start:
        return 0.0
    return min((time.time() - gesture_start[name]) / hold_sec, 1.0)

# ═══════════════════════════════════════════════════════════
#  TRANSITION MACHINE  (FIST ↔ PALM)
# ═══════════════════════════════════════════════════════════
def check_transition(current):
    """
    Detects when user transitions from FIST→PALM (maximise) or
    PALM→FIST (quit).  The previous gesture is remembered for
    PREV_GESTURE_WINDOW seconds so the user has time to make the
    transition naturally.  Each transition fires only once per occurrence.
    """
    global prev_gesture, prev_gesture_t, transition_done
    now = time.time()

    fired = None
    if current == "PALM" and prev_gesture == "FIST":
        key = "F2P"
        if key not in transition_done or now - transition_done[key] > 2.0:
            if now - prev_gesture_t < PREV_GESTURE_WINDOW:
                transition_done[key] = now
                fired = "FIST_TO_PALM"

    elif current == "FIST" and prev_gesture == "PALM":
        key = "P2F"
        if key not in transition_done or now - transition_done[key] > 2.0:
            if now - prev_gesture_t < PREV_GESTURE_WINDOW:
                transition_done[key] = now
                fired = "PALM_TO_FIST"

    # Maintain prev_gesture memory
    if current != prev_gesture:
        prev_gesture   = current
        prev_gesture_t = now

    return fired

# ═══════════════════════════════════════════════════════════
#  DISPATCH
# ═══════════════════════════════════════════════════════════
def dispatch(gesture, lm):
    global cursor_x, cursor_y
    global last_click_time, last_app_time, last_volume_time, last_media_time
    global scroll_prev_y, scroll_last_t

    now = time.time()

    # ── transition check: FIST<->PALM ───────────────────────
    transition = check_transition(gesture)
    if transition == "FIST_TO_PALM":
        win_maximise()
        flash("⬜  WINDOW MAXIMISED")
        return
    if transition == "PALM_TO_FIST":
        win_quit()
        flash("✕  QUIT APP  (Cmd+Q)")
        return

    # ── cursor ───────────────────────────────────────────────
    if gesture == "POINT":
        sf = traffic_lerp(cursor_x, cursor_y)
        cursor_x = lerp(cursor_x, (1.0 - lm[8].x) * SCREEN_W, sf)
        cursor_y = lerp(cursor_y, lm[8].y * SCREEN_H, sf)
        pyautogui.moveTo(cursor_x, cursor_y)
        cursor_history.append((int(cursor_x), int(cursor_y)))
        scroll_prev_y = None   # reset scroll tracking when not scrolling

    # ── TWO fingers → scroll  (vertical motion of index+middle midpoint) ──
    elif gesture == "TWO":
        # midpoint Y of index tip (lm8) and middle tip (lm12)
        mid_y = (lm[8].y + lm[12].y) / 2.0

        if scroll_prev_y is not None:
            delta = mid_y - scroll_prev_y   # positive = hand moved down
            if abs(delta) > SCROLL_DEADZONE and now - scroll_last_t > SCROLL_COOLDOWN:
                if delta < 0:
                    # fingers moved UP → scroll page UP
                    pyautogui.scroll(SCROLL_LINES)
                    flash("▲  SCROLL UP")
                else:
                    # fingers moved DOWN → scroll page DOWN
                    pyautogui.scroll(-SCROLL_LINES)
                    flash("▼  SCROLL DOWN")
                scroll_last_t = now

        scroll_prev_y = mid_y

    # ── clicks ───────────────────────────────────────────────
    elif gesture == "PINCH":
        if now - last_click_time > CLICK_COOLDOWN:
            pyautogui.click()
            last_click_time = now
            flash("● LEFT CLICK")
        scroll_prev_y = None

    elif gesture == "THREE":
        if now - last_click_time > CLICK_COOLDOWN:
            pyautogui.rightClick()
            last_click_time = now
            flash("● RIGHT CLICK")
        scroll_prev_y = None

    # ── window ───────────────────────────────────────────────
    elif gesture == "THUMB":
        if confirm_gesture("THUMB", THUMB_HOLD_SEC):
            win_minimise()
            flash("▼  MINIMISE WINDOW")
            gesture_start.clear()
        scroll_prev_y = None

    # ── media / apps ─────────────────────────────────────────
    elif gesture == "FIST":
        if confirm_gesture("FIST") and now - last_media_time > APP_COOLDOWN:
            media_play_pause()
            last_media_time = now
            flash("⏯  MEDIA PLAY/PAUSE")
        scroll_prev_y = None

    elif gesture == "PALM":
        if confirm_gesture("PALM") and now - last_app_time > APP_COOLDOWN:
            open_app("Google Chrome")
            last_app_time = now
            flash("⬡  LAUNCH CHROME")
        scroll_prev_y = None

    elif gesture == "IDX_RING":
        if confirm_gesture("IDX_RING") and now - last_app_time > APP_COOLDOWN:
            open_app("Visual Studio Code")
            last_app_time = now
            flash("⬡  OPEN VS CODE")
        scroll_prev_y = None

    elif gesture == "IDX_PINKY":
        if confirm_gesture("IDX_PINKY") and now - last_app_time > APP_COOLDOWN:
            open_app("Spotify")
            last_app_time = now
            flash("⬡  OPEN SPOTIFY")
        scroll_prev_y = None

    # ── volume ───────────────────────────────────────────────
    elif gesture == "MIDDLE":
        if now - last_volume_time > VOLUME_COOLDOWN:
            volume_down()
            last_volume_time = now
        scroll_prev_y = None

    elif gesture == "PINKY":
        if now - last_volume_time > VOLUME_COOLDOWN:
            volume_up()
            last_volume_time = now
        scroll_prev_y = None

    else:
        scroll_prev_y = None

# ═══════════════════════════════════════════════════════════
#  HUD RENDERING
# ═══════════════════════════════════════════════════════════
HOLD_SECS = {
    "FIST"     : GESTURE_HOLD_SEC,
    "PALM"     : GESTURE_HOLD_SEC,
    "THUMB"    : THUMB_HOLD_SEC,
    "IDX_RING" : GESTURE_HOLD_SEC,
    "IDX_PINKY": GESTURE_HOLD_SEC,
}

def draw_hud(frame, gesture, lm_list, fps):
    global scan_y
    h, w = frame.shape[:2]
    now  = time.time()
    font = cv2.FONT_HERSHEY_SIMPLEX

    # scanlines
    ov = frame.copy()
    for y in range(0, h, 4):
        cv2.line(ov, (0, y), (w, y), (0, 0, 0), 1)
    cv2.addWeighted(ov, 0.12, frame, 0.88, 0, frame)

    # scan beam
    scan_y = (scan_y + SCAN_SPEED) % h
    cv2.line(frame, (0, scan_y), (w, scan_y), C_CYAN, 1)
    for off, a in [(3, 0.22), (7, 0.08)]:
        tmp = frame.copy()
        for dy in [-off, off]:
            sy = scan_y + dy
            if 0 <= sy < h:
                cv2.line(tmp, (0, sy), (w, sy), C_CYAN, 1)
        cv2.addWeighted(tmp, a, frame, 1 - a, 0, frame)

    # glow rect helper
    def glow_rect(p1, p2, color, tk=2, layers=3):
        for i in range(layers, 0, -1):
            tmp = frame.copy()
            cv2.rectangle(tmp, p1, p2, color, tk + (layers - i) * 2)
            cv2.addWeighted(tmp, 0.07 * i, frame, 1 - 0.07 * i, 0, frame)
        cv2.rectangle(frame, p1, p2, color, tk)

    # border — turns orange near traffic-light zone
    near_tl = cursor_x < TRAFFIC_ZONE_X and cursor_y < TRAFFIC_ZONE_Y
    glow_rect((8, 8), (w - 8, h - 8), C_ORANGE if near_tl else C_CYAN)

    # corner brackets
    for (cx, cy, dx, dy) in [(8,8,1,1),(w-8,8,-1,1),(8,h-8,1,-1),(w-8,h-8,-1,-1)]:
        cv2.line(frame, (cx, cy), (cx + dx*30, cy), C_MAGENTA, 3)
        cv2.line(frame, (cx, cy), (cx, cy + dy*30), C_MAGENTA, 3)

    # precision mode badge
    if near_tl:
        sf = traffic_lerp(cursor_x, cursor_y)
        cv2.putText(frame, f"PRECISION  LERP={sf:.3f}",
                    (w//2 - 90, 56), font, 0.42, C_ORANGE, 1)

    # hand landmarks
    if lm_list:
        for a_i, b_i in mp_hands.HAND_CONNECTIONS:
            ax, ay = int(lm_list[a_i].x * w), int(lm_list[a_i].y * h)
            bx, by = int(lm_list[b_i].x * w), int(lm_list[b_i].y * h)
            tmp = frame.copy()
            cv2.line(tmp, (ax, ay), (bx, by), C_CYAN, 3)
            cv2.addWeighted(tmp, 0.28, frame, 0.72, 0, frame)
            cv2.line(frame, (ax, ay), (bx, by), C_CYAN, 1)
        for i, lm in enumerate(lm_list):
            px, py = int(lm.x * w), int(lm.y * h)
            col = C_MAGENTA if i in TIP else C_CYAN
            r   = 6 if i in TIP else 3
            tmp = frame.copy()
            cv2.circle(tmp, (px, py), r+4, col, -1)
            cv2.addWeighted(tmp, 0.16, frame, 0.84, 0, frame)
            cv2.circle(frame, (px, py), r, col, -1)
            cv2.circle(frame, (px, py), r+1, C_WHITE, 1)

    # gesture label box (bottom-left)
    label = SHORT_LABELS.get(gesture, "—")
    ts = cv2.getTextSize(label, font, 0.55, 2)[0]
    lx, ly = 20, h - 60
    cv2.rectangle(frame, (lx-6, ly-ts[1]-8), (lx+ts[0]+10, ly+6), (10,12,18), -1)
    glow_rect((lx-6, ly-ts[1]-8), (lx+ts[0]+10, ly+6), C_MAGENTA, 1, 2)
    cv2.putText(frame, label, (lx, ly), font, 0.55, C_MAGENTA, 2)

    # flash message (centre)
    if hud_msg and (now - hud_msg_t) < HUD_DUR:
        fade = 1.0 - (now - hud_msg_t) / HUD_DUR
        col  = tuple(int(c * fade) for c in C_GREEN)
        mts  = cv2.getTextSize(hud_msg, font, 0.6, 1)[0]
        cv2.putText(frame, hud_msg,
                    (w//2 - mts[0]//2, h//2), font, 0.6, col, 1)

    # hold progress bar (bottom)
    if gesture in gesture_start and gesture in HOLD_SECS:
        pct  = hold_pct(gesture, HOLD_SECS[gesture])
        bx, by_ = 20, h - 28
        bw  = w - 40
        cv2.rectangle(frame, (bx, by_), (bx+bw, by_+6), (25,25,25), -1)
        bar_col = C_GREEN if pct >= 1.0 else C_YELLOW
        cv2.rectangle(frame, (bx, by_), (bx+int(bw*pct), by_+6), bar_col, -1)
        cv2.putText(frame, "HOLD", (bx, by_-4), font, 0.35, C_YELLOW, 1)

    # transition hints + scroll hint
    if gesture == "FIST":
        cv2.putText(frame, "open palm → MAXIMISE",
                    (w - 230, h - 60), font, 0.38, C_CYAN, 1)
    elif gesture == "PALM":
        cv2.putText(frame, "close fist → QUIT APP",
                    (w - 232, h - 60), font, 0.38, C_CYAN, 1)
    elif gesture == "TWO":
        cv2.putText(frame, "move UP = scroll up  |  DOWN = scroll down",
                    (w - 320, h - 60), font, 0.36, C_YELLOW, 1)

    # top info
    raw_lbl = f"[ {gesture} ]"
    rts = cv2.getTextSize(raw_lbl, font, 0.45, 1)[0]
    cv2.putText(frame, raw_lbl, (w - rts[0] - 20, 32), font, 0.45, C_CYAN, 1)
    cv2.putText(frame, f"FPS {fps:.0f}", (20, 34), font, 0.50, C_GREEN, 1)
    cv2.putText(frame, f"CUR {int(cursor_x):5d},{int(cursor_y):5d}",
                (20, 54), font, 0.40, C_DIM, 1)

    title = "GESTURE CTRL // CYBERPUNK HUD v3"
    tts = cv2.getTextSize(title, font, 0.43, 1)[0]
    cv2.putText(frame, title, (w//2 - tts[0]//2, 32), font, 0.43, C_CYAN, 1)

    # cursor trail
    if len(cursor_history) >= 2:
        pts = list(cursor_history)
        for i in range(1, len(pts)):
            a   = i / len(pts)
            col = (int(C_MAGENTA[0]*a), int(C_MAGENTA[1]*a), int(C_MAGENTA[2]*a))
            fx  = int(pts[i][0]   / SCREEN_W * w)
            fy  = int(pts[i][1]   / SCREEN_H * h)
            fx0 = int(pts[i-1][0] / SCREEN_W * w)
            fy0 = int(pts[i-1][1] / SCREEN_H * h)
            cv2.line(frame, (fx0, fy0), (fx, fy), col, 2)

    return frame

# ═══════════════════════════════════════════════════════════
#  LEGEND
# ═══════════════════════════════════════════════════════════
def print_legend():
    for l in [
        "",
        "╔══════════════════════════════════════════════════════╗",
        "║    GESTURE CONTROL — CYBERPUNK HUD v4                ║",
        "╠══════════════════════════════════════════════════════╣",
        "║  ☝  1 finger          →  Move cursor                 ║",
        "║       (slows near ●●● close/min/max buttons)         ║",
        "║  🤏  Pinch             →  Left click                  ║",
        "║  3️⃣  3 fingers         →  Right click                 ║",
        "║  ✌  2 fingers  ↑      →  Scroll UP                  ║",
        "║  ✌  2 fingers  ↓      →  Scroll DOWN                ║",
        "╠══════════════════════════════════════════════════════╣",
        "║  ✊→🖐 Fist then Palm  →  Maximise  (Ctrl+Cmd+F)    ║",
        "║  🖐→✊ Palm then Fist  →  Quit app  (Cmd+Q)         ║",
        "║  👍  Thumb only hold   →  Minimise  (Cmd+M)          ║",
        "╠══════════════════════════════════════════════════════╣",
        "║  ✊  Fist hold         →  Media play/pause            ║",
        "║  🖐  Palm hold         →  Launch Chrome               ║",
        "║  🤘  Index+Ring        →  Open VS Code               ║",
        "║  🤙  Index+Pinky       →  Open Spotify               ║",
        "║  🖕  Middle finger     →  Volume down                 ║",
        "║  🤙  Pinky only        →  Volume up                  ║",
        "╠══════════════════════════════════════════════════════╣",
        "║  Press  Q  in HUD window to quit                     ║",
        "╚══════════════════════════════════════════════════════╝",
        "",
    ]: print(l)

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    global scan_y, frame_count, fps_display, fps_t0

    print_legend()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    cap.set(cv2.CAP_PROP_FPS,          60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Check Privacy → Camera in System Preferences.")
        sys.exit(1)

    cv2.namedWindow("GESTURE CTRL", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("GESTURE CTRL", WIN_W, WIN_H)

    bg = np.full((CAM_H, CAM_W, 3), C_BG, dtype=np.uint8)

    while True:
        ret, raw = cap.read()
        if not ret:
            continue

        frame_count += 1
        now = time.time()
        if frame_count % 20 == 0:
            fps_display = 20.0 / (now - fps_t0 + 1e-9)
            fps_t0 = now

        frame = cv2.flip(raw, 1)   # mirror — finger left = cursor left
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = hands.process(rgb)
        rgb.flags.writeable = True

        display = bg.copy()
        cv2.addWeighted(cv2.resize(frame, (CAM_W, CAM_H)), 0.27, display, 0.73, 0, display)

        gesture = "NONE"
        lm_list = None

        if result.multi_hand_landmarks:
            lm_list = result.multi_hand_landmarks[0].landmark
            gesture = classify_gesture(lm_list)

            for k in list(gesture_start.keys()):
                if k != gesture:
                    del gesture_start[k]

            dispatch(gesture, lm_list)
        else:
            gesture_start.clear()
            # still update transition machine so prev_gesture ages out
            check_transition("NONE")

        display = draw_hud(display, gesture, lm_list, fps_display)

        cv2.imshow("GESTURE CTRL", display)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("\n[✓] Gesture control stopped.")


if __name__ == "__main__":
    main()