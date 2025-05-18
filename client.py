
"""
Ultimate Agent: runs on each PC at startup, enrolls user via voice once,
then sequentially every 3 minutes: 15 s keystroke/mouse capture + send,
followed by 10 s voice auth capture + send.
"""
import os
import json
import time
import io
import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
from pynput import mouse, keyboard
from testscripts.device_fingerprint import get_device_fingerprint
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox

# --- Configuration ---
SERVICE_URL = "https://services.vistaa.xyz"
VOICE_ENROLL_ENDPOINT  = f"{SERVICE_URL}/voice/enroll"
VOICE_IDENTIFY_ENDPOINT = f"{SERVICE_URL}/voice/identify"
KM_PUSH_ENDPOINT       = f"{SERVICE_URL}/km/push_batch"
REGISTER_PC_ENDPOINT   = f"{SERVICE_URL}/register_pc"
REGISTER_USER_ENDPOINT = f"{SERVICE_URL}/register_user"
MAP_PC_USER_ENDPOINT   = f"{SERVICE_URL}/map_pc_user"

CONFIG_PATH = os.path.expanduser("~/.ultimate_agent_config.json")
TEST_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How much wood would a woodchuck chuck?",
    "Peter Piper picked a peck of pickled peppers.",
    "I scream, you scream, we all scream for ice cream.",
    "A stitch in time saves nine.",
    "Reading maketh a full man.",
    "To be or not to be, that is the question.",
    "All that glitters is not gold.",
    "Better late than never."
]

# --- Device Fingerprint ---
fp = get_device_fingerprint()
PC_ID = fp.get("fingerprint", "unknown_pc")

# --- Load/Save Config ---
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"enrolled": False, "user_id": None}

def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f)

config = load_config()

# --- Register PC & User ---
def register_pc():
    try:
        requests.post(REGISTER_PC_ENDPOINT, data={"pc_id": PC_ID, "fingerprint": PC_ID}, timeout=5)
    except:
        pass

def register_user(user_id):
    try:
        requests.post(REGISTER_USER_ENDPOINT, data={"user_id": user_id}, timeout=5)
    except:
        pass

def map_pc_user(user_id):
    try:
        requests.post(MAP_PC_USER_ENDPOINT, data={"pc_id": PC_ID, "user_id": user_id}, timeout=5)
    except:
        pass

# --- Audio Recording ---
SAMPLERATE = 16000
CHANNELS = 1

def record_audio(duration):
    audio = sd.rec(int(duration * SAMPLERATE), samplerate=SAMPLERATE, channels=CHANNELS)
    sd.wait()
    buf = io.BytesIO()
    sf.write(buf, audio, SAMPLERATE, format="WAV")
    buf.seek(0)
    return buf

# --- Voice Enrollment UI ---
class VoiceEnrollUI(tk.Tk):
    def __init__(self, user_id):
        super().__init__()
        self.withdraw()
        self.user_id = user_id

    def enroll(self):
        files = {}
        for i, sentence in enumerate(np.random.choice(TEST_SENTENCES, 3, replace=False), start=1):
            messagebox.showinfo("Recording Prompt", f"Sentence {i}/3:\n{sentence}")
            buf = record_audio(duration=4)
            files[f"file{i}"] = (f"{self.user_id}_{i}.wav", buf, "audio/wav")
        resp = requests.post(VOICE_ENROLL_ENDPOINT, files=files, data={"user_id": self.user_id})
        resp.raise_for_status()
        messagebox.showinfo("Enroll Success", f"{self.user_id} enrolled.")

# --- Event Capture ---
events = []
lock = False

def on_move(x, y):
    events.append((time.time(), "move", {"x": x, "y": y}))

def on_click(x, y, button, pressed):
    et = "click_down" if pressed else "click_up"
    events.append((time.time(), et, {"x": x, "y": y, "button": str(button)}))

def on_scroll(x, y, dx, dy):
    events.append((time.time(), "scroll", {"x": x, "y": y, "dx": dx, "dy": dy}))

def on_key_press(key):
    code = getattr(key, 'vk', getattr(key, 'value', 0)) or 0
    events.append((time.time(), "key_down", {"key_code": code}))

def on_key_release(key):
    code = getattr(key, 'vk', getattr(key, 'value', 0)) or 0
    events.append((time.time(), "key_up", {"key_code": code}))

# --- Main Loop ---
def main():
    register_pc()
    if not config.get("enrolled"):
        root = tk.Tk(); root.withdraw()
        uid = simpledialog.askstring("Enroll", "Enter new user ID:")
        if not uid:
            print("User ID required. Exiting.")
            return
        register_user(uid)
        map_pc_user(uid)
        VoiceEnrollUI(uid).enroll()
        config.update({"enrolled": True, "user_id": uid})
        save_config(config)
    else:
        map_pc_user(config["user_id"])

    # Start listeners
    mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll).start()
    keyboard.Listener(on_press=on_key_press, on_release=on_key_release).start()

    print(f"Agent active on {PC_ID}, user {config['user_id']}")

    try:
        while True:
            cycle_start = time.time()
            # 1) Capture & send KM for 15s
            print("Capturing KM events for 15s...")
            time.sleep(15)
            km_batch = {
    "device_id": PC_ID,
    "events": [
        {"timestamp": t, "event_type": et, "data": d}  # Removed device_id from individual events
        for t, et, d in events[-200:]
    ]
}
            try:
                r = requests.post(KM_PUSH_ENDPOINT, json=km_batch)
                print("KM response:", r.json())
            except Exception as e:
                print("KM error:", e)

            # 2) Voice auth for 10s
            print("Capturing voice for 10s auth...")
            buf = record_audio(duration=10)
            files = {"file": ("auth.wav", buf, "audio/wav")}
            data = {"pc_id": PC_ID, "threshold": 0.40}  # Add PC_ID
            try:
                r = requests.post(VOICE_IDENTIFY_ENDPOINT, files=files, data=data)
                print("Voice auth:", r.json())
            except Exception as e:
                print("Voice error:", e)

            # 3) Sleep until 3 min cycle
            elapsed = time.time() - cycle_start
            to_sleep = max(0, 180 - elapsed)
            print(f"Cycle done, sleeping {to_sleep:.1f}s...")
            time.sleep(to_sleep)
    except KeyboardInterrupt:
        print("Shutting down agent.")

if __name__ == '__main__':
    main()
