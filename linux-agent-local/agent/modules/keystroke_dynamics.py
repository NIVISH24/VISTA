# from pynput import keyboard
# import time
# import json
# from datetime import datetime

# class KeystrokeMonitor:
#     def __init__(self, callback):
#         self.callback = callback
#         self.last_key_time = None
#         self.key_sequence = []
#         self.listener = None

#     def _on_press(self, key):
#         try:
#             current_time = time.time()
#             if self.last_key_time is not None:
#                 interval = current_time - self.last_key_time
#                 self.key_sequence.append({
#                     "key": key.char if hasattr(key, 'char') else str(key),
#                     "interval": interval,
#                     "time": datetime.now().isoformat()
#                 })
                
#                 # Log every 10 keystrokes
#                 if len(self.key_sequence) >= 10:
#                     self.callback({
#                         "type": "keystrokes",
#                         "data": self.key_sequence
#                     })
#                     self.key_sequence = []
            
#             self.last_key_time = current_time
#         except Exception as e:
#             print(f"Keystroke error: {e}")

#     def start(self):
#         self.listener = keyboard.Listener(on_press=self._on_press)
#         self.listener.start()

#     def stop(self):
#         if self.listener:
#             self.listener.stop()

from pynput import keyboard
import time
import threading
from datetime import datetime

class KeystrokeMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.key_sequence = []
        self.is_recording = False
        self.listener = None
        self._start_recording_cycle()  # Start the 15-sec cycle

    def _start_recording_cycle(self):
        """Start a timer to begin recording every 15 seconds."""
        threading.Timer(15, self._start_recording_cycle).start()  # Restart cycle
        self._start_recording()  # Start recording for 2 secs

    def _start_recording(self):
        """Start recording for 7 seconds."""
        if not self.is_recording:
            self.is_recording = True
            print("Recording keystrokes...")
            threading.Timer(7, self._stop_recording).start()  # Stop after 2 secs

    def _stop_recording(self):
        """Stop recording and log events."""
        if self.is_recording:
            self.is_recording = False
            if self.key_sequence:
                self.callback({
                    "type": "keystrokes",
                    "data": self.key_sequence
                })
                self.key_sequence = []  # Reset for next cycle
            print("Recording stopped. Waiting for next cycle...")

    def _on_press(self, key):
        """Record a keystroke if currently recording."""
        if self.is_recording:
            try:
                current_time = time.time()
                key_data = {
                    "key": key.char if hasattr(key, 'char') else str(key),
                    "time": datetime.now().isoformat()
                }
                self.key_sequence.append(key_data)
            except Exception as e:
                print(f"Keystroke error: {e}")

    def start(self):
        """Start the keyboard listener."""
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def stop(self):
        """Stop the listener and timers."""
        if self.listener:
            self.listener.stop()