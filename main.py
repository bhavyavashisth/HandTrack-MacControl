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
from mediapipe.tasks.python.vision.core import image as mp_image
import numpy as np
import time
import platform
import sys

from src.config import CAM_W, CAM_H, WIN_W, WIN_H, C_BG
from src.gesture import classify_gesture
from src.hud import draw_hud
from src.dispatch import dispatch
import src.state as state

if platform.system() != "Darwin":
    print("[WARN] Designed for macOS. Some features may not work on other OS.")

import pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# ═══════════════════════════════════════════════════════════
#  MEDIAPIPE CALLBACK
# ═══════════════════════════════════════════════════════════
def on_live_result(result, output_image, timestamp_ms):
    """Callback for MediaPipe live stream detection."""
    if result.hand_landmarks:
        lm_list = result.hand_landmarks[0]
        gesture = classify_gesture(lm_list)
        with state.result_lock:
            state.latest_gesture = gesture
            state.latest_lm_list = lm_list
            state.latest_callback_time = timestamp_ms
    else:
        with state.result_lock:
            state.latest_gesture = "NONE"
            state.latest_lm_list = None
            state.latest_callback_time = timestamp_ms

# ═══════════════════════════════════════════════════════════
#  LEGEND
# ═══════════════════════════════════════════════════════════
def print_legend():
    """Print control legend to console."""
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
    """Main entry point for gesture control system."""
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

    # Initialize MediaPipe Hand Landmarker
    mp_hand_options = mp.tasks.vision.HandLandmarkerOptions(
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        base_options=mp.tasks.BaseOptions(model_asset_path='hand_landmarker.task'),
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.6,
        result_callback=on_live_result,
    )
    hands = mp.tasks.vision.HandLandmarker.create_from_options(mp_hand_options)

    bg = np.full((CAM_H, CAM_W, 3), C_BG, dtype=np.uint8)
    last_dispatch_time = 0
    
    try:
        while True:
            ret, raw = cap.read()
            if not ret:
                continue

            state.frame_count += 1
            now = time.time()
            if state.frame_count % 20 == 0:
                state.fps_display = 20.0 / (now - state.fps_t0 + 1e-9)
                state.fps_t0 = now

            frame = cv2.flip(raw, 1)   # mirror — finger left = cursor left
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            mp_frame = mp_image.Image(mp_image.ImageFormat.SRGB,
                                    np.ascontiguousarray(rgb))
            timestamp_ms = int(now * 1000)
            hands.detect_async(mp_frame, timestamp_ms)

            display = bg.copy()
            cv2.addWeighted(cv2.resize(frame, (CAM_W, CAM_H)), 0.27, display, 0.73, 0, display)

            with state.result_lock:
                gesture = state.latest_gesture
                lm_list = state.latest_lm_list
                callback_time = state.latest_callback_time

            if callback_time != last_dispatch_time:
                last_dispatch_time = callback_time
                if lm_list:
                    # Clear old gestures
                    for k in list(state.gesture_start.keys()):
                        if k != gesture:
                            del state.gesture_start[k]
                    dispatch(gesture, lm_list)
                else:
                    state.clear_gesture_start()
                    from src.dispatch import check_transition
                    check_transition("NONE")

            display = draw_hud(display, gesture, lm_list, state.fps_display)

            cv2.imshow("GESTURE CTRL", display)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    except KeyboardInterrupt:
        print("\n[✓] Gesture control stopping...")
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("\n[✓] Gesture control stopped.")


if __name__ == "__main__":
    main()
