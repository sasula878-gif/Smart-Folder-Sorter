import os, shutil, time, threading, sys, tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageDraw
import pystray

# Попытка импорта для автозагрузки
try:
    import winreg
    IS_WIN = True
except:
    IS_WIN = False

APP_NAME = "SmartSorter"
DL_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

# Правила сортировки
RULES = {
    "Presentations": [".pptx", ".ppt", ".pps"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar"],
    "Video": [".mp4", ".mkv", ".mov", ".avi"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Installers": [".exe", ".msi"],
    "Code": [".py", ".js", ".html", ".css", ".json"],
}

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.sort(event.src_path)

    def sort(self, path):
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1].lower()
        
        for folder, exts in RULES.items():
            if ext in exts:
                dest = os.path.join(DL_DIR, folder)
                os.makedirs(dest, exist_ok=True)
                # Ждем окончания загрузки
                time.sleep(2)
                try:
                    shutil.move(path, os.path.join(dest, name))
                except:
                    pass
                break

def add_to_startup():
    if not IS_WIN: return
    path = os.path.realpath(__file__)
    cmd = f'"{sys.executable}" "{path}" --silent' if path.endswith(".py") else f'"{path}" --silent'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
    except: pass

def start_logic():
    if not os.path.exists(DL_DIR): return
    obs = Observer()
    obs.schedule(Handler(), DL_DIR, recursive=False)
    obs.start()
    while True: time.sleep(1)

def quit_app(icon):
    icon.stop()
    os._exit(0)

if __name__ == "__main__":
    if "--silent" not in sys.argv:
        add_to_startup()
        root = tk.Tk(); root.withdraw()
        messagebox.showinfo("Smart Sorter", "Работаю в трее!")
        root.destroy()
    
    threading.Thread(target=start_logic, daemon=True).start()
    
    img = Image.new('RGB', (64, 64), (30, 30, 30))
    d = ImageDraw.Draw(img); d.rectangle([10, 10, 54, 54], fill=(0, 120, 215))
    
    icon = pystray.Icon(APP_NAME, img, "Smart Sorter", menu=pystray.Menu(
        pystray.MenuItem('Выход', quit_app)
    ))
    icon.run()