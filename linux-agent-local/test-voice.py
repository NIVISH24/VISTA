from agent.modules.voice_snapshots import VoiceMonitor
from agent.utils.local_logger import LocalLogger

logger = LocalLogger()
voice_monitor = VoiceMonitor(
    logger=logger,
    output_dir="/var/log/linux-agent/voice",  # Must exist and be writable
    sample_rate=44100,
    duration=5  # 5 seconds snapshot
)

voice_monitor.take_snapshot()
