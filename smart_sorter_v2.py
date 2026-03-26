import customtkinter as ctk
import json
import os
import time
import threading
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- КОНФИГУРАЦИЯ ---
SETTINGS_FILE = "settings.json"

class MoverHandler(FileSystemEventHandler):
    def __init__(self, watch_path, date_sort):
        self.watch_path = watch_path
        self.date_sort = date_sort
        self.extensions = {
            ".pptx": "Presentations", ".ppt": "Presentations",
            ".jpg": "Images", ".png": "Images", ".pdf": "Documents",
            ".zip": "Archives", ".mp4": "Video"
        }

    def on_modified(self, event):
        for filename in os.listdir(self.watch_path):
            extension = os.path.splitext(filename)[1].lower()
            if extension in self.extensions:
                source = os.path.join(self.watch_path, filename)
                
                # Логика подпапок по датам (v2.0)
                folder_name = self.extensions[extension]
                if self.date_sort:
                    date_folder = time.strftime("%Y-%m")
                    dest_folder = os.path.join(self.watch_path, folder_name, date_folder)
                else:
                    dest_folder = os.path.join(self.watch_path, folder_name)

                os.makedirs(dest_folder, exist_ok=True)
                
                # Ждем, пока файл докачается
                time.sleep(2) 
                try:
                    os.rename(source, os.path.join(dest_folder, filename))
                    print(f"Перемещено: {filename}")
                except Exception as e:
                    print(f"Ошибка: {e}")

class SmartSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Folder Sorter v2.0")
        self.geometry("600x500")
        
        self.settings = {"watch_path": os.path.expanduser("~/Downloads"), "startup": False, "date_sort": False}
        self.load_settings()

        # Интерфейс
        self.label = ctk.CTkLabel(self, text="Управление Сортировкой 2.0", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        # Выбор папки
        self.f_frame = ctk.CTkFrame(self)
        self.f_frame.pack(fill="x", padx=30, pady=10)
        self.f_label = ctk.CTkLabel(self.f_frame, text=f"Путь: {self.settings['watch_path']}", wraplength=300)
        self.f_label.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(self.f_frame, text="Изменить", width=80, command=self.change_folder).pack(side="right", padx=10)

        # Настройки
        self.sw_date = ctk.CTkSwitch(self, text="Сортировать по датам (Год-Месяц)", command=self.save_settings)
        self.sw_date.pack(pady=10)
        if self.settings["date_sort"]: self.sw_date.select()

        # Кнопка Старт/Стоп
        self.observer = None
        self.btn_status = ctk.CTkButton(self, text="ЗАПУСТИТЬ", fg_color="green", command=self.toggle_service, height=50)
        self.btn_status.pack(pady=30)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f: self.settings.update(json.load(f))

    def save_settings(self):
        self.settings["date_sort"] = self.sw_date.get()
        with open(SETTINGS_FILE, "w") as f: json.dump(self.settings, f, indent=4)

    def change_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.settings["watch_path"] = path
            self.f_label.configure(text=f"Путь: {path}")
            self.save_settings()

    def start_observer(self):
        event_handler = MoverHandler(self.settings["watch_path"], self.settings["date_sort"])
        self.observer = Observer()
        self.observer.schedule(event_handler, self.settings["watch_path"], recursive=False)
        self.observer.start()
        while self.observer:
            time.sleep(1)

    def toggle_service(self):
        if self.observer:
            self.observer.stop()
            self.observer = None
            self.btn_status.configure(text="ЗАПУСТИТЬ", fg_color="green")
        else:
            self.btn_status.configure(text="ОСТАНОВИТЬ (РАБОТАЕТ...)", fg_color="red")
            # Запускаем слежку в отдельном потоке, чтобы окно не зависло
            threading.Thread(target=self.start_observer, daemon=True).start()

if __name__ == "__main__":
    app = SmartSorterApp()
    app.mainloop()