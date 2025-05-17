# from pynput import mouse
# import time
# import json
# from datetime import datetime

# class MouseMonitor:
#     def __init__(self, callback):
#         self.callback = callback
#         self.last_event_time = None
#         self.mouse_events = []
#         self.listener = None

#     def _on_move(self, x, y):
#         self._record_event('move', x, y)

#     def _on_click(self, x, y, button, pressed):
#         self._record_event('click', x, y, button=button.name, pressed=pressed)

#     def _on_scroll(self, x, y, dx, dy):
#         self._record_event('scroll', x, y, dx=dx, dy=dy)

#     def _record_event(self, event_type, x, y, **kwargs):
#         current_time = time.time()
#         event_data = {
#             "type": event_type,
#             "x": x,
#             "y": y,
#             "time": datetime.now().isoformat(),
#             **kwargs
#         }
        
#         if self.last_event_time is not None:
#             event_data["interval"] = current_time - self.last_event_time
        
#         self.mouse_events.append(event_data)
#         self.last_event_time = current_time
        
#         # Log every 20 events
#         if len(self.mouse_events) >= 20:
#             self.callback({
#                 "type": "mouse_events",
#                 "data": self.mouse_events
#             })
#             self.mouse_events = []

#     def start(self):
#         self.listener = mouse.Listener(
#             on_move=self._on_move,
#             on_click=self._on_click,
#             on_scroll=self._on_scroll
#         )
#         self.listener.start()

#     def stop(self):
#         if self.listener:
#             self.listener.stop()

from pynput import mouse
import time
import threading
from datetime import datetime

class MouseMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.mouse_events = []
        self.is_recording = False
        self.listener = None
        self._start_recording_cycle()  # Start the 15-sec cycle

    def _start_recording_cycle(self):
        """Start a timer to begin recording every 15 seconds."""
        threading.Timer(15, self._start_recording_cycle).start()  # Restart cycle
        self._start_recording()  # Start recording for 2 secs

    def _start_recording(self):
        """Start recording for 2 seconds."""
        if not self.is_recording:
            self.is_recording = True
            print("Recording started...")
            threading.Timer(2, self._stop_recording).start()  # Stop after 2 secs

    def _stop_recording(self):
        """Stop recording and log events."""
        if self.is_recording:
            self.is_recording = False
            if self.mouse_events:
                self.callback({
                    "type": "mouse_events",
                    "data": self.mouse_events
                })
                self.mouse_events = []  # Reset for next cycle
            print("Recording stopped. Waiting for next cycle...")

    def _on_move(self, x, y):
        if self.is_recording:
            self._record_event('move', x, y)

    def _on_click(self, x, y, button, pressed):
        if self.is_recording:
            self._record_event('click', x, y, button=button.name, pressed=pressed)

    def _on_scroll(self, x, y, dx, dy):
        if self.is_recording:
            self._record_event('scroll', x, y, dx=dx, dy=dy)

    def _record_event(self, event_type, x, y, **kwargs):
        """Record an event with timestamp."""
        event_data = {
            "type": event_type,
            "x": x,
            "y": y,
            "time": datetime.now().isoformat(),
            **kwargs
        }
        self.mouse_events.append(event_data)

    def start(self):
        """Start the mouse listener."""
        self.listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.listener.start()

    def stop(self):
        """Stop the listener and timers."""
        if self.listener:
            self.listener.stop()