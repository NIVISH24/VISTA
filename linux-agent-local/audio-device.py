import sounddevice as sd
print(sd.query_devices())  # Is "plughw:1,0" listed?
devices = sd.query_devices()
print(f"Device {4}: {devices[4]['name']} (Inputs: {devices[4]['max_input_channels']})")
device_info = sd.query_devices(4)
print(f"Supported sample rates: {device_info['default_samplerate']}")
# If this doesn't show rates, try:
print(sd.query_hostapis())  # Check ALSA/PulseAudio backend config