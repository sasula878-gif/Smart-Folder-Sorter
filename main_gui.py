import customtkinter as ctk
import json
import os
from tkinter import filedialog

SETTINGS_FILE = "settings.json"

class SmartSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.title("Smart Folder Sorter v2.0")
        self.geometry("600x450")
        ctk.set_appearance_mode("dark")

        # Значения по умолчанию
        self.settings = {
            "watch_path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "startup": False,
            "date_sort": False
        }
        self.load_settings() # Загружаем, если файл уже есть

        # --- ИНТЕРФЕЙС ---
        self.label = ctk.CTkLabel(self, text="Панель управления v2.0", font=("Arial", 22, "bold"))
        self.label.pack(pady=20)

        # Блок выбора папки
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill="x", padx=30, pady=10)
        
        self.folder_label = ctk.CTkLabel(self.folder_frame, text=f"Папка: {self.settings['watch_path']}", wraplength=350)
        self.folder_label.pack(side="left", padx=15, pady=10)
        
        self.btn_change = ctk.CTkButton(self.folder_frame, text="Выбрать", width=80, command=self.change_folder)
        self.btn_change.pack(side="right", padx=15)

        # Переключатели (Связываем их с нашими настройками)
        self.sw_startup = ctk.CTkSwitch(self, text="Автозагрузка (Windows Registry)", command=self.save_settings)
        self.sw_startup.pack(pady=15)
        if self.settings["startup"]: self.sw_startup.select()

        self.sw_date = ctk.CTkSwitch(self, text="Сортировать по датам (Месяц/Год)", command=self.save_settings)
        self.sw_date.pack(pady=15)
        if self.settings["date_sort"]: self.sw_date.select()

        # Кнопка Запуска
        self.is_running = False
        self.btn_status = ctk.CTkButton(self, text="ЗАПУСТИТЬ МОНИТОРИНГ", 
                                        fg_color="#2ecc71", hover_color="#27ae60", 
                                        height=45, font=("Arial", 14, "bold"),
                                        command=self.toggle_service)
        self.btn_status.pack(pady=40)

    # --- ЛОГИКА ---
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                self.settings.update(json.load(f))

    def save_settings(self):
        # Обновляем словарь перед сохранением
        self.settings["startup"] = self.sw_startup.get()
        self.settings["date_sort"] = self.sw_date.get()
        
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_unicode=False)
        print("Настройки сохранены!")

    def change_folder(self):
        new_path = filedialog.askdirectory()
        if new_path:
            self.settings["watch_path"] = new_path
            self.folder_label.configure(text=f"Папка: {new_path}")
            self.save_settings()

    def toggle_service(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_status.configure(text="ОСТАНОВИТЬ", fg_color="#e74c3c", hover_color="#c0392b")
            # Сюда мы прикрутим запуск твоего watchdog из версии 1.0
        else:
            self.btn_status.configure(text="ЗАПУСТИТЬ МОНИТОРИНГ", fg_color="#2ecc71", hover_color="#27ae60")

if __name__ == "__main__":
    app = SmartSorterApp()
    app.mainloop()