import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image
import requests
import threading
import io

class FaceRecognitionTester:
    def __init__(self, root, server_url="http://localhost:3002"):
        self.root = root
        self.server_url = server_url
        self.cap = cv2.VideoCapture(0)
        self.captured_images = []
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Face Recognition Tester")
        
        # User ID input
        self.user_id_frame = ttk.Frame(self.root)
        self.user_id_frame.pack(pady=10)
        
        self.user_id_label = ttk.Label(self.user_id_frame, text="User ID:")
        self.user_id_label.pack(side=tk.LEFT)
        
        self.user_id_entry = ttk.Entry(self.user_id_frame, width=25)
        self.user_id_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(pady=10)
        
        self.enroll_btn = ttk.Button(
            self.btn_frame, 
            text="Enroll",
            command=lambda: self.toggle_mode("enroll")
        )
        self.enroll_btn.pack(side=tk.LEFT, padx=5)
        
        self.identify_btn = ttk.Button(
            self.btn_frame,
            text="Identify",
            command=lambda: self.toggle_mode("identify")
        )
        self.identify_btn.pack(side=tk.LEFT, padx=5)
        
        self.action_btn = ttk.Button(
            self.root,
            text="Start Capture",
            command=self.start_action,
            state=tk.DISABLED
        )
        self.action_btn.pack(pady=10)
        
        self.mode = None
        
    def toggle_mode(self, mode):
        self.mode = mode
        self.captured_images = []
        self.action_btn.config(state=tk.NORMAL)
        
        if mode == "enroll":
            self.user_id_entry.config(state=tk.NORMAL)
            self.action_btn.config(text="Capture 3 Photos")
        else:
            self.user_id_entry.config(state=tk.DISABLED)
            self.action_btn.config(text="Capture Photo")
            
    def start_action(self):
        if self.mode == "enroll":
            threading.Thread(target=self.capture_enrollment).start()
        else:
            threading.Thread(target=self.identify).start()
            
    def capture_enrollment(self):
        for i in range(3):
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.captured_images.append(frame)
                messagebox.showinfo("Info", f"Captured photo {i+1}/3")
                
        self.send_enrollment()
        
    def send_enrollment(self):
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please enter a User ID")
            return

        # Capture 3 frames
        frames = []
        for _ in range(3):
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)

        # Prepare files in the required format
        files = []
        for i, frame in enumerate(frames, start=1):
            pil_img = Image.fromarray(frame)
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files.append((f'file{i}', (f'img{i}.jpg', img_bytes, 'image/jpeg')))

        try:
            response = requests.post(
                f"{self.server_url}/enroll",
                files=files,
                data={'user_id': user_id}
            )
            messagebox.showinfo("Result", response.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.reset_ui()
        
    def identify(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame)
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            try:
                response = requests.post(
                    f"{self.server_url}/identify",
                    files={'file': ('identify.jpg', img_bytes, 'image/jpeg')},
                    data={'threshold': 0.5}
                )
                messagebox.showinfo("Result", response.text)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        self.reset_ui()
        
    def reset_ui(self):
        self.mode = None
        self.captured_images = []
        self.action_btn.config(state=tk.DISABLED)
        self.user_id_entry.delete(0, tk.END)
        
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionTester(root)
    root.mainloop()