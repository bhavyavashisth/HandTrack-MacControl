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

### 1️⃣ Prerequisites
This project requires **Python**.

### 2️⃣ Create a Virtual Environment
It is highly recommended to use a virtual environment to keep your dependencies organized.

```bash
#clone the repo.
git clone https://github.com/bhavyavashisth/HandTrack-MacControl.git
# Create the environment
python3.11 -m venv gesture_env

```
Activate the enviourment with-

For mac:

`source gesture_env/bin/activate`

For windows:

`./gesture_env/Scripts/Activate.ps1`

### 3️⃣ Install Dependencies

While your environment is active, install the necessary AI and automation libraries:
```bash
pip install -r requirements.txt
```
### 4️⃣. System Permissions
```
 For the script to control your mouse, you must manually grant permissions in System Settings > Privacy & Security:

    Camera: Allow your Terminal to access the camera for hand tracking.

    Accessibility: Toggle Terminal (or VS Code) ON. This allows the script to move the cursor and click.
```

🛠️ Usage
1. Open your terminal and navigate to your project folder.
2. Run the script:
   
```bash
cd HandTrack-MacControl
python3 main.py

```
3. Press 'Q' while focusing on the HUD window to exit.
## 🎨 Customization

Want to disable the bright transition flash? Find the flash() calls in the code and comment them out:
```bash
# flash("⬜  WINDOW MAXIMISED")  
```
