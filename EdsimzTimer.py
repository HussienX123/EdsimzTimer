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
import winsound
import hashlib
import time
import sys
import subprocess
import psutil

# Get the absolute path to the script's directory

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
        winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)

def pause_timer():
    global running
    running = False
    save_data()
    winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)


def restart_timer():
    global time_left, running
    if mode == "countdown":
        time_left = timer_duration  # Reset to the selected duration
    elif mode == "stopwatch":
        time_left = 0  # Reset stopwatch to 0
    running = False
    time_label.config(text=format_time(time_left))
    save_data()
    winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)
    
def toggle_always_on_top():
    root.attributes("-topmost", not root.attributes("-topmost"))
    winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)

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
    if not os.path.exists(LOCAL_VERSION_FILE):
        print("Local version file not found. Downloading latest version...")
        try:
            # Download the latest version file
            response = requests.get(VERSION_URL)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            
            # Save the downloaded content to the local version file
            with open(LOCAL_VERSION_FILE, "w") as file:
                file.write(response.text)
            
            print("Latest version file downloaded and saved.")
        except Exception as e:
            print(f"Error downloading version file: {e}")
            return {"version": "0.0"}  # Return default version if download fails
    
    # Read the local version file
    try:
        with open(LOCAL_VERSION_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error reading version file: {e}")
        return {"version": "0.0"}  # Return default version if the file is not valid JSON

def download_update(url, filename, progress_callback=None):
    print("Downloading update...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                file.flush()  # Ensure data is written to disk
                downloaded_size += len(chunk)
                if progress_callback:
                    progress_callback(downloaded_size, total_size)
        
        print("Download complete!")
        print(f"Downloaded file size: {os.path.getsize(filename)} bytes")
        print(f"Expected file size: {total_size} bytes")
        print(f"File hash (SHA256): {calculate_file_hash(filename)}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading update: {e}")
        return False

def calculate_file_hash(filename, algorithm="sha256"):
    """Calculate the hash of a file."""
    hash_func = hashlib.new(algorithm)
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def apply_update(zip_path):
    print("Extracting update...")
    if not os.path.exists(zip_path):
        messagebox.showinfo('apply update ', f"Error: File not found: {zip_path}")
        return
    
    if not is_zipfile(zip_path):
        messagebox.showinfo('apply update ', f"Error: File is not a valid ZIP file: {zip_path}")
        return
    
    # Extract to a temporary folder
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(TEMP_FOLDER)
        messagebox.showinfo('apply update ', "Update extracted to temporary folder.")
        
        # Debug: Print the contents of the TEMP_FOLDER
        messagebox.showinfo('apply update ', f"Contents of {TEMP_FOLDER}: {os.listdir(TEMP_FOLDER)}")
        
        # Move files from the temp folder to the application directory
        def is_file_in_use(file_path):
            """Check if a file is in use by another process."""
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    for file in proc.info['open_files']:
                        if file.path == file_path:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return False


        # Example usage in the file move loop
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        for item in os.listdir(TEMP_FOLDER):
            src = os.path.join(TEMP_FOLDER, item)
            dst = os.path.join(BASE_DIR, item)
            print(f"Moving {src} to {dst}")  # Debug: Print source and destination paths
            
            if not os.path.exists(src):
                print(f"Error: Source file does not exist: {src}")
                continue
            
            if is_file_in_use(src):
                print(f"Error: File is in use: {src}")
                messagebox.showerror('apply update ', f"File is in use: {src}. Please close any programs using this file.")
                return
            
            if os.path.exists(dst):
                try:
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                except PermissionError as e:
                    messagebox.showerror('apply update ', f"Permission denied: {e}. Please run the application as an administrator.")
                    return
            
            try:
                shutil.move(src, dst)
                print(f"Moved {src} to {dst} successfully.")
            except Exception as e:
                print(f"Error moving {src} to {dst}: {e}")
                messagebox.showerror('apply update ', f"Error moving files: {e}")
                return   
        
        # Update the version.json file
        latest_version = get_latest_version()
        if latest_version:
            with open(LOCAL_VERSION_FILE, "w") as file:
                json.dump(latest_version, file)
                messagebox.showinfo('apply update ', "Test changing the json file version")
        
        # Notify the user and restart the application
        answer = messagebox.askyesno(title='Update',
                message='A new version has been installed. The application will now restart.')
        if answer:
            root.destroy()
        else:
            root.destroy()

    except zipfile.BadZipFile:
        messagebox.showerror('apply update ', f"Error: File is not a valid ZIP file: {zip_path}")
    except Exception as e:
        messagebox.showerror('apply update ', f"Error extracting update: {e}")

def is_zipfile(filename):
    """Check if the file is a valid ZIP file."""
    return zipfile.is_zipfile(filename)

def show_update_prompt(latest_version):
    # Create a custom dialog for the update prompt
    update_window = ttk.Toplevel(root, bg="black")
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
    progress_window_width = 400
    progress_window_height = 100
    center_window(progress_window, progress_window_width, progress_window_height)
    progress_window.resizable(False, False)

    # Make the progress window modal
    progress_window.grab_set()

    # Disable the main application window
    root.withdraw()  # Hide the main window

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
            root.deiconify()  # Restore the main window
            
            # Add a small delay to ensure the file is fully written
            time.sleep(1)  # Wait for 1 second
            
            # Check if the downloaded file is valid
            zip_path = os.path.join(UPDATE_FOLDER, "update.zip")
            if is_zipfile(zip_path):
                apply_update(zip_path)
            else:
                messagebox.showerror("Error", "The downloaded file is not a valid ZIP file.")

    # Start the download
    os.makedirs(UPDATE_FOLDER, exist_ok=True)
    zip_path = os.path.join(UPDATE_FOLDER, "update.zip")
    if not download_update(download_url, zip_path, update_progress):
        progress_window.destroy()
        root.deiconify()  # Restore the main window
        messagebox.showerror("Error", "Failed to download the update.")

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
    message_window = ttk.Toplevel(root, bg="black")
    message_window.title(title)
    message_window_width = 300
    message_window_height = 100
    center_window(message_window, message_window_width, message_window_height)  # Center the window
    message_window.resizable(False, False)
    message_window.configure(background="black")  # Set the background to black
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
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
style.configure("Pause.TButton", font=("Arial", 10), background="#ff5733", foreground="black", relief='flat', highlightthickness=0, bd=0)

# Style for the Restart button
style.configure("Restart.TButton", font=("Arial", 10), background="#3498db", foreground="black", relief='flat', highlightthickness=0, bd=0)

# Style for the Keep on Top button
style.configure("KeepOnTop.TButton", font=("Arial", 10), background="#9b59b6", foreground="black", relief='flat', highlightthickness=0, bd=0)

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