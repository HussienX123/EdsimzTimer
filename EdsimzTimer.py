import requests
import zipfile
import os
import json
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# GitHub raw version.json URL
VERSION_URL = "https://raw.githubusercontent.com/HussienX123/EdsimzTimer/refs/heads/main/dist/version.json"
LOCAL_VERSION_FILE = "version.json"
UPDATE_FOLDER = "updates"
DATA_FILE = "data.json"

# Pomodoro Timer Logic
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"time_left": 1500, "running": False}  # Default 25 min

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump({"time_left": time_left, "running": running}, file)

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def update_timer():
    global time_left
    if running and time_left > 0:
        time_left -= 1
        time_label.config(text=format_time(time_left))
        save_data()
        root.after(1000, update_timer)

def start_timer():
    global running
    if not running:
        running = True
        update_timer()

def pause_timer():
    global running
    running = False
    save_data()

def restart_timer():
    global time_left, running
    time_left = 1500  # Reset to 25 minutes
    running = False
    time_label.config(text=format_time(time_left))
    save_data()

def toggle_always_on_top():
    root.attributes("-topmost", not root.attributes("-topmost"))

def get_latest_version():
    try:
        response = requests.get(VERSION_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching version info: {e}")
        return None

def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            return json.load(file)
    return {"version": "0.0"}  # Default version if no local file exists

def download_update(url, filename):
    print("Downloading update...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    print("Download complete!")

def apply_update(zip_path):
    print("Extracting update...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(".")  # Extract to the current directory
    print("Update applied successfully!")

def check_for_updates():
    latest_version = get_latest_version()
    local_version = get_local_version()

    if not latest_version:
        print("Could not fetch update info.")
        return

    latest_ver = float(latest_version["version"])
    local_ver = float(local_version["version"])

    if latest_ver > local_ver:
        print(f"New version available: {latest_ver}")
        os.makedirs(UPDATE_FOLDER, exist_ok=True)
        zip_path = os.path.join(UPDATE_FOLDER, "update.zip")

        download_update(latest_version["download_url"], zip_path)
        apply_update(zip_path)

        # Save new version info
        with open(LOCAL_VERSION_FILE, "w") as file:
            json.dump(latest_version, file)

        messagebox.showinfo("Update", "A new version has been installed. Restart the application to apply changes.")
        return True  # Indicate update was applied
    else:
        print("No updates available.")
        return False

# Load saved data
data = load_data()
time_left = data["time_left"]
running = data["running"]

# GUI Setup with ttkbootstrap
root = ttk.Window(themename="darkly")
root.title("Edsimz Timer Pro Max")
root.geometry("400x300")
root.resizable(False, False)

# UI Elements
title_label = ttk.Label(root, text="Working", font=("Arial", 20))
title_label.pack(pady=10)

time_label = ttk.Label(root, text=format_time(time_left), font=("Arial", 40))
time_label.pack(pady=20)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

start_button = ttk.Button(button_frame, text="Start", command=start_timer, bootstyle=SUCCESS)
start_button.grid(row=0, column=0, padx=5)

pause_button = ttk.Button(button_frame, text="Pause", command=pause_timer, bootstyle=WARNING)
pause_button.grid(row=0, column=1, padx=5)

restart_button = ttk.Button(button_frame, text="Restart", command=restart_timer, bootstyle=INFO)
restart_button.grid(row=0, column=2, padx=5)

keep_top_button = ttk.Button(root, text="Keep on Top", command=toggle_always_on_top, bootstyle=SECONDARY)
keep_top_button.pack(pady=10)

# Check for updates when the application starts
check_for_updates()

root.mainloop()