import sounddevice as sd
import numpy as np
from datetime import datetime
from scipy.io.wavfile import write
import os
import time
import threading

class VoiceMonitor:
    def __init__(self, logger, output_dir="/var/log/linux-agent/voice", 
                 sample_rate=44100, duration=5, interval=15,device=None):
        self.logger = logger
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.duration = duration  # Recording duration in seconds
        self.interval = interval  # Time between recordings in seconds
        self.device = device  # <<< ADD THIS
        self.recording = False
        self.monitoring = False
        self.frames = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def _record_callback(self, indata, frames, time, status):
        if status:
            error_msg = f"Recording error: {status}"
            self.logger.log_event({
                "module": "voice_monitor",
                "event": "recording_error",
                "error": error_msg
            })
        if self.recording:
            self.frames.append(indata.copy())

    def _take_recording(self):
        try:
            self.recording = True
            self.frames = []
            
            timestamp = datetime.now().isoformat()
            self.logger.log_event({
                "module": "voice_monitor",
                "event": "recording_started",
                "timestamp": timestamp
            })
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._record_callback,
                dtype='float32',
                device=self.device
            ):
                sd.sleep(self.duration * 1000)
            
            if self.frames:
                audio_data = np.concatenate(self.frames)
                
                # Generate filename with timestamp
                filename = datetime.now().strftime("%Y%m%d_%H%M%S.wav")
                filepath = os.path.join(self.output_dir, filename)
                
                # Save as WAV file
                write(filepath, self.sample_rate, audio_data)
                
                # Log the recording event
                self.logger.log_event({
                    "module": "voice_monitor",
                    "event": "recording_saved",
                    "filepath": filepath,
                    "duration": self.duration,
                    "sample_rate": self.sample_rate,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            self.logger.log_event({
                "module": "voice_monitor",
                "event": "recording_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        finally:
            self.recording = False

    def start_monitoring(self):
        if self.monitoring:
            self.logger.log_event({
                "module": "voice_monitor",
                "event": "monitoring_already_running",
                "timestamp": datetime.now().isoformat()
            })
            return
            
        self.monitoring = True
        self.logger.log_event({
            "module": "voice_monitor",
            "event": "monitoring_started",
            "timestamp": datetime.now().isoformat(),
            "interval": self.interval,
            "duration": self.duration
        })
        
        def monitor_loop():
            while self.monitoring:
                self._take_recording()
                # Wait for the remaining time until next interval
                time_to_wait = max(0, self.interval - self.duration)
                for _ in range(int(time_to_wait)):
                    if not self.monitoring:
                        break
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.logger.log_event({
            "module": "voice_monitor",
            "event": "monitoring_stopped",
            "timestamp": datetime.now().isoformat()
        })
    def take_snapshot(self):
        self._take_recording()
