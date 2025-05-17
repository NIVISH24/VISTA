import os
import sys
import signal
import atexit
import time
from datetime import datetime

class SystemEventMonitor:
    def __init__(self, callback):
        self.callback = callback
        self._shutting_down = False
        self.setup_handlers()

    def _log_event(self, event_type, details=None):
        if not self._shutting_down:
            event_data = {
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            self.callback(event_data)

    def _shutdown_handler(self, signum, frame):
        self._shutting_down = True
        self._log_event("shutdown", {"signal": signum})
        os._exit(0)  # Use os._exit() instead of sys.exit()

    def _reboot_handler(self, signum, frame):
        self._shutting_down = True
        self._log_event("reboot", {"signal": signum})
        os._exit(0)

    def setup_handlers(self):
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._reboot_handler)
        atexit.register(self._log_event, "normal_termination")