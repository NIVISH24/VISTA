import time
import threading
import platform
import requests
from pynput import mouse, keyboard

# --- Globals ---
events = []
DEVICE_ID = platform.node()
SERVER_URL = "http://192.168.79.75:8000/push_batch"
BATCH_INTERVAL = 2  # seconds
MAX_EVENTS = 1000
SEND_WINDOW = 200

# --- Listeners ---
def on_move(x, y):
    events.append((time.time(), "move", {"x": x, "y": y}))

def on_click(x, y, button, pressed):
    et = "click_down" if pressed else "click_up"
    events.append((time.time(), et, {"x": x, "y": y, "button": str(button)}))

def on_scroll(x, y, dx, dy):
    events.append((time.time(), "scroll", {"x": x, "y": y, "dx": dx, "dy": dy}))

def on_key_press(key):
    try:
        code = key.vk if hasattr(key, 'vk') else key.value.vk
    except AttributeError:
        code = 0
    events.append((time.time(), "key_down", {"key_code": code}))

def on_key_release(key):
    try:
        code = key.vk if hasattr(key, 'vk') else key.value.vk
    except AttributeError:
        code = 0
    events.append((time.time(), "key_up", {"key_code": code}))

# Start listeners
mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll).start()
keyboard.Listener(on_press=on_key_press, on_release=on_key_release).start()

# --- Batch Sender ---
def send_batch():
    global events
    while True:
        time.sleep(BATCH_INTERVAL)
        if not events:
            continue
        # select last SEND_WINDOW events
        window = events[-SEND_WINDOW:]
        payload = {
            "device_id": DEVICE_ID,
            "events": [
                {"device_id": DEVICE_ID, "timestamp": t, "event_type": et, "data": d}
                for t, et, d in window
            ]
        }
        try:
            response = requests.post(SERVER_URL, json=payload)
            print(f"Sent {len(window)} events, server returned:", response.json())
        except Exception as e:
            print("Error sending to server:", e)
        # keep only recent MAX_EVENTS
        events = events[-MAX_EVENTS:]

# Start the sender thread
threading.Thread(target=send_batch, daemon=True).start()

# --- Main Loop ---
def main():
    print("Client running. Device:", DEVICE_ID)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down client.")

if __name__ == '__main__':
    main()