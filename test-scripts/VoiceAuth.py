import tkinter as tk
from tkinter import simpledialog, messagebox
import threading, time, random, io
import requests
import sounddevice as sd
import soundfile as sf
import numpy as np

API_URL = "http://localhost:8000"
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

class VoiceAuthGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Auth Client")
        self.geometry("500x250")

        tk.Button(self, text="Enroll User",    command=self.enroll_user).pack(pady=15)
        tk.Button(self, text="Identify Voice", command=self.identify_voice).pack(pady=15)

    def enroll_user(self):
        user_id = simpledialog.askstring("Enroll", "Enter new user ID:")
        if not user_id:
            return

        sentences = random.sample(TEST_SENTENCES, 3)
        buffers = []  # will hold (BytesIO, duration)

        for idx, sentence in enumerate(sentences, start=1):
            messagebox.showinfo("Recording Prompt",
                                f"Sentence {idx} of 3:\n\n{sentence}")
            result = self.record_audio()
            if result is None:
                return  # cancelled or too short
            buffers.append(result)

        # build payload and send
        files = {}
        for i, (bio, dur) in enumerate(buffers, start=1):
            bio.seek(0)
            files[f"file{i}"] = (f"{user_id}_{i}.wav", bio, "audio/wav")
        data = {"user_id": user_id}

        try:
            resp = requests.post(f"{API_URL}/enroll", files=files, data=data)
            resp.raise_for_status()
            j = resp.json()
            messagebox.showinfo("Enroll Success",
                                f"Status: {j['status']} for user: {j['user_id']}")
        except Exception as e:
            messagebox.showerror("Error", f"Enrollment failed:\n{e}")
        finally:
            for bio, _ in buffers:
                bio.close()

    def identify_voice(self):
        sentence = random.choice(TEST_SENTENCES)
        messagebox.showinfo("Identify",
                            f"Please speak the following:\n\n{sentence}")
        result = self.record_audio()
        if result is None:
            return

        bio, _ = result
        bio.seek(0)
        files = {"file": ("identify.wav", bio, "audio/wav")}
        try:
            resp = requests.post(f"{API_URL}/identify", files=files)
            resp.raise_for_status()
            j = resp.json()
            if j["result"] == "known":
                msg = f"✅ Known: {j['user_id']} (score: {j['score']:.2f})"
            else:
                msg = f"❌ Unknown (max score: {j['max_score']:.2f})"
            messagebox.showinfo("Identification Result", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Identification failed:\n{e}")
        finally:
            bio.close()

    def record_audio(self):
        samplerate = 16000
        channels = 1
        recorded = []
        recording = threading.Event()
        start_time = [0.0]

        # create modal dialog
        win = tk.Toplevel(self)
        win.title("Recording")
        tk.Label(win, text="Press Start, speak, then Stop").pack(pady=5)
        timer_label = tk.Label(win, text="00:00")
        timer_label.pack()

        def update_timer():
            if recording.is_set():
                elapsed = time.time() - start_time[0]
                mins, secs = divmod(int(elapsed), 60)
                timer_label.config(text=f"{mins:02d}:{secs:02d}")
                win.after(200, update_timer)

        def sd_callback(indata, frames, t, status):
            if status:
                print("Status:", status)
            if recording.is_set():
                recorded.append(indata.copy())

        def start_cb():
            recorded.clear()
            recording.set()
            start_time[0] = time.time()
            update_timer()
            try:
                win.stream = sd.InputStream(
                    samplerate=samplerate,
                    channels=channels,
                    callback=sd_callback
                )
                win.stream.start()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot start recording:\n{e}")
                win.destroy()

        def stop_cb():
            if recording.is_set():
                recording.clear()
                win.stream.stop()
                dur = time.time() - start_time[0]
                # assemble buffer
                if dur < 0.5:
                    win._result = None
                else:
                    audio = np.concatenate(recorded, axis=0)
                    bio = io.BytesIO()
                    sf.write(bio, audio, samplerate, format="WAV")
                    win._result = (bio, dur)
                win.destroy()

        # buttons
        frm = tk.Frame(win)
        frm.pack(pady=10)
        tk.Button(frm, text="Start", command=start_cb).pack(side=tk.LEFT, padx=5)
        tk.Button(frm, text="Stop",  command=stop_cb).pack(side=tk.LEFT, padx=5)

        win.grab_set()            # make modal
        self.wait_window(win)     # wait until it's destroyed

        # after dialog closes
        result = getattr(win, "_result", None)
        if result:
            _, dur = result
            messagebox.showinfo("Recording Finished",
                                f"Duration: {dur:.2f} seconds")
        return result

if __name__ == "__main__":
    app = VoiceAuthGUI()
    app.mainloop()
