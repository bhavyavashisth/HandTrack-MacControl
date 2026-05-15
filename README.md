# Gesture-control
# 🖱️ Mac Air Mouse Control (Cyberpunk HUD v4)

[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-000000?logo=apple&logoColor=white)](https://apple.com)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Control your Mac in the air.** This project turns your webcam into a high-precision gesture tracker, allowing you to move the cursor, click, scroll, and manage windows without ever touching your desk.

---

## ⚡ Quick Features
* **Air Navigation**: Move your index finger to control the system cursor.
* **Precision Mode**: Automatically slows down the cursor near window close/minimize/maximize buttons for pixel-perfect accuracy.
* **Smart Gestures**: Pinch to click, or use a fist-to-palm transition to maximize windows.
* **Cyberpunk HUD**: A cinematic overlay with real-time hand landmarks, scan lines, and live gesture labels.

---

## 🎮 How to Control

| Gesture | Action |
| :--- | :--- |
| ☝ **1 Finger (Index)** | Move Cursor |
| 🤏 **Pinch (Index + Thumb)** | Left Click |
| 3️⃣ **3 Fingers** | Right Click |
| ✌ **2 Fingers (Vertical)** | Scroll Up / Down |
| ✊ → 🖐 **Fist to Palm** | Maximize Window (Ctrl+Cmd+F) |
| 🖐 → ✊ **Palm to Fist** | Quit Application (Cmd+Q) |
| 👍 **Thumb Hold** | Minimize Window (Cmd+M) |
| ✊ **Fist Hold** | Media Play/Pause |

---

## 🚀 Setup & Installation

### 1. Prerequisites
You must have **Python 3.11** installed. Newer versions like 3.14 are not yet compatible with MediaPipe.

### 2. Create Environment
```bash
python3.11 -m venv gesture_env
source gesture_env/bin/activate

```
### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt

```
4. System Permissions

For the mouse to move, macOS requires you to grant permissions:

    Camera: For hand tracking.

    Accessibility: Go to System Settings > Privacy & Security > Accessibility and toggle Terminal (or VS Code) ON.

🛠️ Usage
1. Open your terminal and navigate to your project folder.
2. Run the script:
```bash
python3 AetherHUD.py

```
3. Press 'Q' while focusing on the HUD window to exit.
## 🎨 Customization

Want to disable the bright transition flash? Find the flash() calls in the code and comment them out:
```bash
# flash("⬜  WINDOW MAXIMISED")  
```
