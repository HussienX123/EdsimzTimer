import requests
import zipfile
import os
import json
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style

# GitHub raw version.json URL
VERSION_URL = "https://raw.githubusercontent.com/HussienX123/EdsimzTimer/refs/heads/main/dist/version.json"
LOCAL_VERSION_FILE = "version.json"
UPDATE_FOLDER = "updates"
TEMP_FOLDER = "temp_update"
DATA_FILE = "data.json"

global total_hours_finished
total_hours_finished = 0  

# Pomodoro Timer Logic
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"time_left": 1500, "running": False, "mode": "countdown", "timer_duration": 1500, "total_hours_finished": 0}  # Default values

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump({"time_left": time_left, "running": running, "mode": mode, "timer_duration": timer_duration, "total_hours_finished": total_hours_finished}, file)

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def update_timer():
    global running, total_hours_finished 
    global time_left
    if running:
        if mode == "countdown":
            if time_left > 0:
                time_left -= 1
            else:
                running = False
                total_hours_finished += timer_duration / 3600  # Add finished time in hours
                show_custom_message("Timer", f"Time's up!\nTotal hours finished: {total_hours_finished:.2f}")
                restart_timer()
        elif mode == "stopwatch":
            time_left += 1
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
    if mode == "countdown":
        time_left = timer_duration  # Reset to the selected duration
    elif mode == "stopwatch":
        time_left = 0  # Reset stopwatch to 0
    running = False
    time_label.config(text=format_time(time_left))
    save_data()
    
def toggle_always_on_top():
    root.attributes("-topmost", not root.attributes("-topmost"))

def show_settings():
    # Timer Duration Label and Entry
    style = Style()  # You can try other themes as well, like "superhero", "cyborg", etc.

    # Define custom style for Radiobuttons
    style.configure("Custom.TRadiobutton",
                    background="black",
                    foreground="white",
                    font=("Arial", 12))
    settings_window = ttk.Toplevel(root, bg="black")
    settings_window.title("Settings")
    settings_window_width = 320
    settings_window_height = 300
    center_window(settings_window, settings_window_width, settings_window_height)
    settings_window.resizable(False, False)
    settings_window.configure(background="black")


    # Make the settings window modal
    settings_window.grab_set()

    duration_label = ttk.Label(settings_window, text="Timer Duration (minutes):", font=("Arial", 12), background="black")
    duration_label.pack(pady=10)

    duration_entry = ttk.Entry(settings_window, font=("Arial", 12), width = 15)
    duration_entry.insert(0, str(timer_duration // 60))  # Convert seconds to minutes
    duration_entry.pack(pady=10)

    # Timer Mode Selection
    mode_label = ttk.Label(settings_window, text="Timer Mode:", font=("Arial", 12) , background="black")
    mode_label.pack(pady=10)

    mode_var = tk.StringVar(value=mode)
    # Create Radiobuttons using the custom style
    countdown_radio = ttk.Radiobutton(settings_window, text="Countdown", variable=mode_var, value="countdown", style='primary.Outline.Toolbutton', width = 10)
    countdown_radio.pack(pady=5)

    stopwatch_radio = ttk.Radiobutton(settings_window, text="Stopwatch", variable=mode_var, value="stopwatch", style='primary.Outline.Toolbutton' , width = 10)
    stopwatch_radio.pack(pady=5)

    # Save Settings Button
    def save_settings():
        global timer_duration, mode, time_left
        try:
            new_duration = int(duration_entry.get()) * 60  # Convert minutes to seconds
            if new_duration <= 0:
                raise ValueError("Duration must be greater than 0")
            timer_duration = new_duration
            mode = mode_var.get()
            if mode == "countdown":
                time_left = timer_duration  # Reset timer to new duration
            elif mode == "stopwatch":
                time_left = 0  # Reset stopwatch to 0
            time_label.config(text=format_time(time_left))
            save_data()
            settings_window.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    save_button = ttk.Button(settings_window, text="Save", command=save_settings, bootstyle=SUCCESS, width = 20)
    save_button.pack(pady=5)

def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the window geometry
    window.geometry(f"{width}x{height}+{x}+{y}")

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

def download_update(url, filename, progress_callback=None):
    print("Downloading update...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0

    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            downloaded_size += len(chunk)
            if progress_callback:
                progress_callback(downloaded_size, total_size)
    print("Download complete!")

def apply_update(zip_path):
    print("Extracting update...")
    # Extract to a temporary folder
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(TEMP_FOLDER)
    print("Update extracted to temporary folder.")

    # Notify the user to restart the application
    messagebox.showinfo("Update", "A new version has been downloaded. Please restart the application to apply the update.")

def show_update_prompt(latest_version):
    # Create a custom dialog for the update prompt
    update_window = ttk.Toplevel(root)
    update_window.title("Update Available")
    update_window_width = 400  # Wider window
    update_window_height = 150
    center_window(update_window, update_window_width, update_window_height)
    update_window.resizable(False, False)

    # Make the update window modal
    update_window.grab_set()

    # Message label
    message_label = ttk.Label(update_window, text="A new version is available. Do you want to update now?", font=("Arial", 12))
    message_label.pack(pady=20)

    # Button frame
    button_frame = ttk.Frame(update_window)
    button_frame.pack(pady=10)

    # Update button
    def on_update():
        update_window.destroy()
        show_download_progress(latest_version["download_url"])

    update_button = ttk.Button(button_frame, text="Update", command=on_update, bootstyle=SUCCESS)
    update_button.pack(side=LEFT, padx=10)

    # Close application button
    def on_close():
        update_window.destroy()
        root.destroy()  # Close the application

    close_button = ttk.Button(button_frame, text="Close Application", command=on_close, bootstyle=DANGER)
    close_button.pack(side=RIGHT, padx=10)

def show_download_progress(download_url):
    # Create a new window for the download progress
    progress_window = ttk.Toplevel(root)
    progress_window.title("Downloading Update")
    progress_window_width = 400  # Wider window
    progress_window_height = 100
    center_window(progress_window, progress_window_width, progress_window_height)
    progress_window.resizable(False, False)

    # Make the progress window modal
    progress_window.grab_set()

    progress_label = ttk.Label(progress_window, text="Downloading update...", font=("Arial", 12))
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_window, orient=HORIZONTAL, length=300, mode="determinate")
    progress_bar.pack(pady=10)

    def update_progress(downloaded_size, total_size):
        progress = int((downloaded_size / total_size) * 100)
        progress_bar["value"] = progress
        progress_label.config(text=f"Downloading... {progress}%")
        if downloaded_size >= total_size:
            progress_window.destroy()
            apply_update(os.path.join(UPDATE_FOLDER, "update.zip"))

    # Start the download
    os.makedirs(UPDATE_FOLDER, exist_ok=True)
    zip_path = os.path.join(UPDATE_FOLDER, "update.zip")
    download_update(download_url, zip_path, update_progress)

def check_for_updates():
    latest_version = get_latest_version()
    local_version = get_local_version()

    if not latest_version:
        print("Could not fetch update info.")
        return

    latest_ver = float(latest_version["version"])
    local_ver = float(local_version["version"])

    if latest_ver > local_ver:
        show_update_prompt(latest_version)
    else:
        print("No updates available.")

def show_custom_message(title, message):
    # Create a custom top-level window
    message_window = ttk.Toplevel(root)
    message_window.title(title)
    message_window_width = 300
    message_window_height = 100
    center_window(message_window, message_window_width, message_window_height)  # Center the window
    message_window.resizable(False, False)
    message_window.configure(background="black")  # Set the background to black
    
    # Make the window always on top
    message_window.attributes("-topmost", True)
    
    # Make the window modal
    message_window.grab_set()
    
    # Add a label for the message
    message_label = ttk.Label(message_window, text=message, font=("Arial", 12), foreground="white", background="black")
    message_label.pack(pady=20)
    
    # Add an OK button to close the window
    ok_button = ttk.Button(message_window, text="OK", command=message_window.destroy, style="Custom.TButton")
    ok_button.pack(pady=10)
# Load saved data
data = load_data()
time_left = data["time_left"]
running = data["running"]
mode = data["mode"]
timer_duration = data["timer_duration"]
total_hours_finished = data.get("total_hours_finished", 0)

# GUI Setup with ttkbootstrap
root = ttk.Window(themename="darkly")
root.title("EDSIMZ TIMER")
root.geometry("450x350")
root.resizable(False, False)
root.configure(background="black")

# UI Elements
title_label = ttk.Label(root, text="EDSIMZ", font=("Arial", 26, "bold"), foreground="#22ff68", background="black")
title_label.pack(pady=6)

time_label = ttk.Label(root, text=format_time(time_left), font=("Arial", 40), background="black")
time_label.pack(pady=15)

# Initialize style
s = ttk.Style()
# Create style used by default for all Frames
s.configure('TFrame', background='black')

button_frame = ttk.Frame(root, style='TFrame')
button_frame.pack(pady=10)

# STYLES
# Define custom styles for each button
style = ttk.Style()

# Style for the Start button
style.configure("Start.TButton", font=("Arial", 10), background="#22ff68", foreground="black" , relief='flat', highlightthickness=0, bd=0)

# Style for the Pause button
style.configure("Pause.TButton", font=("Arial", 10), background="#ff5733", foreground="white", relief='flat', highlightthickness=0, bd=0)

# Style for the Restart button
style.configure("Restart.TButton", font=("Arial", 10), background="#3498db", foreground="white", relief='flat', highlightthickness=0, bd=0)

# Style for the Keep on Top button
style.configure("KeepOnTop.TButton", font=("Arial", 10), background="#9b59b6", foreground="white", relief='flat', highlightthickness=0, bd=0)

# Style for the Settings button
style.configure("Settings.TButton", font=("Arial", 10), background="#2ecc71", foreground="black", relief='flat', highlightthickness=0, bd=0)


# Start Button
start_button = ttk.Button(button_frame, text="Start", command=start_timer, width=6, style="Start.TButton")
start_button.grid(row=0, column=0, padx=5)

# Pause Button
pause_button = ttk.Button(button_frame, text="Pause", command=pause_timer, width=6, style="Pause.TButton")
pause_button.grid(row=0, column=1, padx=5)

# Restart Button
restart_button = ttk.Button(button_frame, text="Restart", command=restart_timer, width=6, style="Restart.TButton")
restart_button.grid(row=0, column=2, padx=5)

# Keep on Top Button
keep_top_button = ttk.Button(root, text="Keep on Top", command=toggle_always_on_top, width=26, style="KeepOnTop.TButton")
keep_top_button.pack(pady=5)

# Settings Button
settings_button = ttk.Button(root, text="Settings", command=show_settings, width=26, style="Settings.TButton")
settings_button.pack(pady=(0,6))

copyright_label = ttk.Label(root, text="made by al-hussienx", font=("Arial", 10, "bold"), foreground="#257a40", background="black")
copyright_label.pack(pady=6)

# Customize hover and active states for each button
style.map("Start.TButton",
          background=[("active", "#1abc9c"), ("pressed", "#16a085")],  # Background color on hover and click
          foreground=[("active", "white"), ("pressed", "white")])       # Text color on hover and click

style.map("Pause.TButton",
          background=[("active", "#e74c3c"), ("pressed", "#c0392b")],
          foreground=[("active", "white"), ("pressed", "white")])

style.map("Restart.TButton",
          background=[("active", "#2980b9"), ("pressed", "#1c5980")],
          foreground=[("active", "white"), ("pressed", "white")])

style.map("KeepOnTop.TButton",
          background=[("active", "#8e44ad"), ("pressed", "#6c3483")],
          foreground=[("active", "white"), ("pressed", "white")])

style.map("Settings.TButton",
          background=[("active", "#27ae60"), ("pressed", "#1e8449")],
          foreground=[("active", "white"), ("pressed", "white")])

# Check for updates when the application starts
check_for_updates()

root.mainloop()