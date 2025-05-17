
import os
import sys
import time
import signal
from datetime import datetime
from daemon import DaemonContext
from .modules.device_fingerprint import get_device_fingerprint
from .modules.usb_monitor import USBMonitor
from .modules.keystroke_dynamics import KeystrokeMonitor
from .modules.mouse_monitor import MouseMonitor
from .modules.voice_snapshots import VoiceMonitor
from .modules.system_events import SystemEventMonitor
from .utils.local_logger import LocalLogger
import systemd.daemon

class LinuxAgent:
    def __init__(self, pidfile):
        self.pidfile = pidfile
        self.logger = LocalLogger()
        
        # Get device fingerprint first
        self.device_fingerprint = get_device_fingerprint()
        
        # Initialize monitors with proper event handling
        self.usb_monitor = USBMonitor(self._create_event_handler("usb"))
        self.keystroke_monitor = KeystrokeMonitor(self._create_event_handler("keystroke"))
        self.mouse_monitor = MouseMonitor(self._create_event_handler("mouse"))
        
        # self.voice_monitor = VoiceMonitor(self._create_event_handler("voice"))
        self.voice_monitor = VoiceMonitor(
            logger=self.logger,
            output_dir="/var/log/linux-agent/voice",  # ensure target directory
            sample_rate=48000,
            duration=5,  # 5 seconds recording
            interval=3600,  # optional: if using continuous monitoring
            device=4
)
        self.system_monitor = SystemEventMonitor(self._create_event_handler("system"))
        
        # Log device fingerprint
        self.logger.log_event({
            "module": "system",
            "type": "device_fingerprint",
            "data": self.device_fingerprint,
            "timestamp": datetime.now().isoformat()
        })

    def _create_event_handler(self, module_name):
        """Helper method to create properly configured event handlers"""
        def handler(event_data):
            try:
                if not isinstance(event_data, dict):
                    event_data = {"data": event_data}
                
                event_data.setdefault("module", module_name)
                event_data.setdefault("timestamp", datetime.now().isoformat())
                event_data["device_fingerprint"] = self.device_fingerprint.get("fingerprint", "unknown")
                
                self.logger.log_event(event_data)
            except Exception as e:
                print(f"Error in {module_name} event handler: {str(e)}")
                self.logger.log_event({
                    "module": "system",
                    "type": "error",
                    "message": f"{module_name} handler failed: {str(e)}",
                    "original_event": str(event_data)[:200]
                })
        return handler

    def run(self):
        """Main agent execution loop"""
        # Start all monitors
        self.usb_monitor.start()
        self.keystroke_monitor.start()
        self.mouse_monitor.start()
        self.system_monitor.setup_handlers()
        
        # Notify systemd we're ready
        systemd.daemon.notify('READY=1')
        
        # Main loop with voice sampling (with error handling)
        last_voice_sample = 0
        while True:
            try:
                current_time = time.time()
                if current_time - last_voice_sample > 10:  # Every hour
                    try:
                        self.voice_monitor.take_snapshot()
                        last_voice_sample = current_time
                    except Exception as e:
                        print(f"Voice snapshot error: {str(e)}")
                        self.logger.log_event({
                            "module": "system",
                            "type": "error",
                            "message": f"Voice snapshot failed: {str(e)}"
                        })
                        last_voice_sample = current_time  # Try again next hour
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.log_event({
                    "module": "system",
                    "type": "shutdown",
                    "message": "Received keyboard interrupt"
                })
                break
                
            except SystemExit:
                self.logger.log_event({
                    "module": "system",
                    "type": "shutdown",
                    "message": "Received system exit signal"
                })
                break
                
            except Exception as e:
                error_msg = f"Main loop error: {str(e)}"
                print(error_msg)
                self.logger.log_event({
                    "module": "system",
                    "type": "error",
                    "message": error_msg
                })
                time.sleep(10)

    def stop(self):
        """Cleanup method to stop all monitors and remove pidfile"""
        self.logger.log_event({
            "module": "system",
            "type": "shutdown",
            "message": "Stopping LinuxAgent"
        })
        
        self.usb_monitor.stop()
        self.keystroke_monitor.stop()
        self.mouse_monitor.stop()
        
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

def create_daemon():
    """Create daemon context with proper signal handling"""
    pidfile = '/var/run/linux-agent.pid'
    context = DaemonContext(
        pidfile=pidfile,
        working_directory=os.getcwd(),
        umask=0o002,
        detach_process=True,
        signal_map={
            signal.SIGTERM: lambda signum, frame: sys.exit(0),
            signal.SIGINT: lambda signum, frame: sys.exit(0)
        }
    )
    return context

def main():
    """Main entry point for the agent"""
    try:
        # Notify systemd we're starting
        systemd.daemon.notify('STATUS=Starting Linux Agent...')
        
        # Create and run agent
        agent = LinuxAgent('/var/run/linux-agent.pid')
        agent.run()
        
    except Exception as e:
        error_msg = f"Agent startup failed: {str(e)}"
        print(error_msg)
        
        # Try to log the error even if logger might not be fully initialized
        try:
            LocalLogger().log_event({
                "module": "system",
                "type": "startup_error",
                "message": error_msg
            })
        except:
            pass
            
        # Notify systemd of failure
        systemd.daemon.notify(f'STATUS={error_msg}')
        systemd.daemon.notify('ERRNO=1')
        raise

if __name__ == "__main__":
    main()