"""
HUD rendering for Gesture Control System.
"""

import cv2
import time
import mediapipe as mp
from src.config import (
    CAM_W, CAM_H, WIN_W, WIN_H, SCAN_SPEED, HUD_DUR,
    C_CYAN, C_MAGENTA, C_YELLOW, C_GREEN, C_ORANGE, C_WHITE, C_DIM, C_BG,
    TIP, TRAFFIC_ZONE_X, TRAFFIC_ZONE_Y, SHORT_LABELS, HOLD_SECS
)
from src.helpers import hold_pct, traffic_lerp
import src.state as state

HAND_CONNECTIONS = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS

def glow_rect(frame, p1, p2, color, tk=2, layers=3):
    """Draw a glowing rectangle effect."""
    h, w = frame.shape[:2]
    for i in range(layers, 0, -1):
        tmp = frame.copy()
        cv2.rectangle(tmp, p1, p2, color, tk + (layers - i) * 2)
        cv2.addWeighted(tmp, 0.07 * i, frame, 1 - 0.07 * i, 0, frame)
    cv2.rectangle(frame, p1, p2, color, tk)

def draw_scanlines(frame):
    """Draw animated scanlines for cyberpunk effect."""
    h, w = frame.shape[:2]
    ov = frame.copy()
    for y in range(0, h, 4):
        cv2.line(ov, (0, y), (w, y), (0, 0, 0), 1)
    cv2.addWeighted(ov, 0.12, frame, 0.88, 0, frame)

def draw_scan_beam(frame):
    """Draw the scanning beam animation."""
    h, w = frame.shape[:2]
    state.scan_y = (state.scan_y + SCAN_SPEED) % h
    cv2.line(frame, (0, state.scan_y), (w, state.scan_y), C_CYAN, 1)
    for off, a in [(3, 0.22), (7, 0.08)]:
        tmp = frame.copy()
        for dy in [-off, off]:
            sy = state.scan_y + dy
            if 0 <= sy < h:
                cv2.line(tmp, (0, sy), (w, sy), C_CYAN, 1)
        cv2.addWeighted(tmp, a, frame, 1 - a, 0, frame)

def draw_border_and_corners(frame):
    """Draw border and corner brackets."""
    h, w = frame.shape[:2]
    # border — turns orange near traffic-light zone
    near_tl = state.cursor_x < TRAFFIC_ZONE_X and state.cursor_y < TRAFFIC_ZONE_Y
    glow_rect(frame, (8, 8), (w - 8, h - 8), C_ORANGE if near_tl else C_CYAN)

    # corner brackets
    for (cx, cy, dx, dy) in [(8,8,1,1),(w-8,8,-1,1),(8,h-8,1,-1),(w-8,h-8,-1,-1)]:
        cv2.line(frame, (cx, cy), (cx + dx*30, cy), C_MAGENTA, 3)
        cv2.line(frame, (cx, cy), (cx, cy + dy*30), C_MAGENTA, 3)

def draw_precision_badge(frame):
    """Draw precision mode indicator."""
    h, w = frame.shape[:2]
    if state.cursor_x < TRAFFIC_ZONE_X and state.cursor_y < TRAFFIC_ZONE_Y:
        sf = traffic_lerp(state.cursor_x, state.cursor_y)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"PRECISION  LERP={sf:.3f}",
                    (w//2 - 90, 56), font, 0.42, C_ORANGE, 1)

def draw_hand_landmarks(frame, lm_list):
    """Draw hand skeleton and landmarks."""
    h, w = frame.shape[:2]
    if not lm_list:
        return

    for connection in HAND_CONNECTIONS:
        a_i, b_i = connection.start, connection.end
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

def draw_gesture_label(frame, gesture):
    """Draw gesture label box at bottom-left."""
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    label = SHORT_LABELS.get(gesture, "—")
    ts = cv2.getTextSize(label, font, 0.55, 2)[0]
    lx, ly = 20, h - 60
    cv2.rectangle(frame, (lx-6, ly-ts[1]-8), (lx+ts[0]+10, ly+6), (10,12,18), -1)
    glow_rect(frame, (lx-6, ly-ts[1]-8), (lx+ts[0]+10, ly+6), C_MAGENTA, 1, 2)
    cv2.putText(frame, label, (lx, ly), font, 0.55, C_MAGENTA, 2)

def draw_flash_message(frame):
    """Draw fading flash message in center."""
    h, w = frame.shape[:2]
    now = time.time()
    if state.hud_msg and (now - state.hud_msg_t) < HUD_DUR:
        font = cv2.FONT_HERSHEY_SIMPLEX
        fade = 1.0 - (now - state.hud_msg_t) / HUD_DUR
        col  = tuple(int(c * fade) for c in C_GREEN)
        mts  = cv2.getTextSize(state.hud_msg, font, 0.6, 1)[0]
        cv2.putText(frame, state.hud_msg,
                    (w//2 - mts[0]//2, h//2), font, 0.6, col, 1)

def draw_hold_progress(frame, gesture):
    """Draw hold progress bar at bottom."""
    h, w = frame.shape[:2]
    if gesture in state.gesture_start and gesture in HOLD_SECS:
        font = cv2.FONT_HERSHEY_SIMPLEX
        pct  = hold_pct(gesture, HOLD_SECS[gesture])
        bx, by_ = 20, h - 28
        bw  = w - 40
        cv2.rectangle(frame, (bx, by_), (bx+bw, by_+6), (25,25,25), -1)
        bar_col = C_GREEN if pct >= 1.0 else C_YELLOW
        cv2.rectangle(frame, (bx, by_), (bx+int(bw*pct), by_+6), bar_col, -1)
        cv2.putText(frame, "HOLD", (bx, by_-4), font, 0.35, C_YELLOW, 1)

def draw_transition_hints(frame, gesture):
    """Draw transition hints and scroll instructions."""
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    if gesture == "FIST":
        cv2.putText(frame, "open palm → MAXIMISE",
                    (w - 230, h - 60), font, 0.38, C_CYAN, 1)
    elif gesture == "PALM":
        cv2.putText(frame, "close fist → QUIT APP",
                    (w - 232, h - 60), font, 0.38, C_CYAN, 1)
    elif gesture == "TWO":
        cv2.putText(frame, "move UP = scroll up  |  DOWN = scroll down",
                    (w - 320, h - 60), font, 0.36, C_YELLOW, 1)

def draw_top_info(frame, gesture, fps):
    """Draw FPS, gesture, cursor position, and title."""
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Raw gesture label
    raw_lbl = f"[ {gesture} ]"
    rts = cv2.getTextSize(raw_lbl, font, 0.45, 1)[0]
    cv2.putText(frame, raw_lbl, (w - rts[0] - 20, 32), font, 0.45, C_CYAN, 1)

    # FPS
    cv2.putText(frame, f"FPS {fps:.0f}", (20, 34), font, 0.50, C_GREEN, 1)

    # Cursor position
    cv2.putText(frame, f"CUR {int(state.cursor_x):5d},{int(state.cursor_y):5d}",
                (20, 54), font, 0.40, C_DIM, 1)

    # Title
    title = "GESTURE CTRL // CYBERPUNK HUD v3"
    tts = cv2.getTextSize(title, font, 0.43, 1)[0]
    cv2.putText(frame, title, (w//2 - tts[0]//2, 32), font, 0.43, C_CYAN, 1)

def draw_cursor_trail(frame):
    """Draw cursor movement trail."""
    h, w = frame.shape[:2]
    import pyautogui
    screen_w, screen_h = pyautogui.size()
    if len(state.cursor_history) >= 2:
        pts = list(state.cursor_history)
        for i in range(1, len(pts)):
            a   = i / len(pts)
            col = (int(C_MAGENTA[0]*a), int(C_MAGENTA[1]*a), int(C_MAGENTA[2]*a))
            fx  = int(pts[i][0]   / screen_w * w)
            fy  = int(pts[i][1]   / screen_h * h)
            fx0 = int(pts[i-1][0] / screen_w * w)
            fy0 = int(pts[i-1][1] / screen_h * h)
            cv2.line(frame, (fx0, fy0), (fx, fy), col, 2)

def draw_hud(frame, gesture, lm_list, fps):
    """Main HUD rendering function."""
    h, w = frame.shape[:2]

    # Effects and overlays
    draw_scanlines(frame)
    draw_scan_beam(frame)
    draw_border_and_corners(frame)
    draw_precision_badge(frame)

    # Hand visualization
    draw_hand_landmarks(frame, lm_list)

    # Information displays
    draw_gesture_label(frame, gesture)
    draw_flash_message(frame)
    draw_hold_progress(frame, gesture)
    draw_transition_hints(frame, gesture)
    draw_top_info(frame, gesture, fps)
    draw_cursor_trail(frame)

    return frame
