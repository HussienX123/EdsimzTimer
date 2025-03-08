import tkinter as tk
import time
import json
import os
from threading import Thread

# Constants
WORK_DURATION = 25 * 60  # 25 minutes
BREAK_DURATION = 5 * 60  # 5 minutes
DATA_FILE = "pomodoro_data.json"

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x300")
        self.root.configure(bg="black")        
        self.load_data()
        
        self.status_label = tk.Label(root, text="work", font=("Arial", 20), fg="white", bg="black")
        self.status_label.pack(pady=5)
        
        self.timer_label = tk.Label(root, text=self.format_time(self.data['time_left']), font=("Arial", 40), fg="white", bg="black")
        self.timer_label.pack(pady=10)
        
        button_frame = tk.Frame(root, bg="black")
        button_frame.pack()
        
        self.start_button = tk.Button(button_frame, text="Start", font=("Arial", 14), command=self.start_timer, bg="white")
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.pause_button = tk.Button(button_frame, text="Start", font=("Arial", 14), command=self.pause_timer, bg="white")
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(button_frame, text="Start", font=("Arial", 14), command=self.reset_timer, bg="white")
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        self.always_on_top_button = tk.Button(root, text="Keep on Top", font=("Arial", 14), command=self.toggle_always_on_top, bg="white")
        self.always_on_top_button.pack(pady=10)
        
        self.running = False
        self.paused = False
        self.time_left = self.data['time_left']
        
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}
        
        # Ensure required keys exist
        if "sessions" not in self.data:
            self.data["sessions"] = 0
        if "time_left" not in self.data:
            self.data["time_left"] = WORK_DURATION
        
        self.time_left = self.data["time_left"]  # Assign loaded time
        self.save_data()
    
    def save_data(self):
        self.data['time_left'] = self.time_left
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
    
    def start_timer(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_button.config(state=tk.DISABLED)
            Thread(target=self.run_timer, daemon=True).start()
    
    def run_timer(self):
        while self.time_left > 0 and self.running:
            if self.paused:
                time.sleep(1)
                continue
            
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02}")
            time.sleep(1)
            self.time_left -= 1
            self.save_data()
            self.root.update()
        
        if self.time_left == 0:
            self.status_label.config(text="Break")
            self.time_left = BREAK_DURATION
            self.running = False
            self.start_button.config(state=tk.NORMAL)
    
    def pause_timer(self):
        if self.running:
            self.paused = not self.paused
            self.status_label.config(text="Paused" if self.paused else "Running")
            self.save_data()
    
    def reset_timer(self):
        self.running = False
        self.paused = False
        self.time_left = WORK_DURATION
        self.save_data()
        self.timer_label.config(text="25:00")
        self.status_label.config(text="work")
        self.start_button.config(state=tk.NORMAL)
    
    def toggle_always_on_top(self):
        current_state = self.root.attributes("-topmost")
        self.root.attributes("-topmost", not current_state)
        self.always_on_top_button.config(text="Keep on Top" if not current_state else "Disable Always on Top")
    
    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"
        
if __name__ == "__main__":
    root = tk.Tk()
    #root.iconbitmap("love.ico")
    app = PomodoroApp(root)
    root.mainloop()