import sounddevice as sd

# Test recording on Device 4
print("Testing recording on Device 4...")
recording = sd.rec(int(5 * 44100), samplerate=44100, channels=1, device=4)
sd.wait()  # Wait for recording to finish
print("✅ Recording successful!")