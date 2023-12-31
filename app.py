import json

import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox

import redis
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import psutil
from PIL import Image

from utility_function import basis_handle_errors, Log
from update_version import Updater

font14 = ("MesloLGS NF", 14)
font12 = ("MesloLGS NF", 12)
nameTab1 = "Runner"
nameTab2 = "Settings"

updater = Updater()
version_app = updater.get_remote_version()

process = None
pids = []
path_delete = None
static_content = []


@basis_handle_errors("CRMStarterApp")
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.default_theme_entry = None
        self.appearance_mode_option_menu = None
        self.scrollbar = None
        self.check_buttons_frame_inner = None
        self.tab_view = None
        self.is_monitoring_stop = False
        self.theme = tk.StringVar()
        self.theme.set("system")
        self.default_theme = tk.StringVar()
        self.default_theme.set("dark-blue")
        self.redis_host_theme = tk.StringVar()
        self.redis_host_theme.set("127.0.0.1")
        self.redis_port_theme = tk.StringVar()
        self.redis_port_theme.set("6379")
        self.host_app = tk.StringVar()
        self.host_app.set("localhost")
        self.download_link_btn = None
        self.button_stop = None
        self.button_start = None
        self.button_delete = None
        self.button_change = None
        self.path_frame_1 = None
        self.alias_frame_1 = None
        self.alias_frame_2 = None
        self.notebook = None
        self.canvas_scrollbar = None
        self.canvas = None
        self.dll_frame_2 = None
        self.bd_frame_2 = None
        self.app_port_frame_2 = None
        self.redis_port_frame_2 = None
        self.pg_port_frame_2 = None
        self.path_frame_2 = None
        self.dll_frame_1 = None
        self.pg_port_frame_1 = None
        self.redis_port_frame_1 = None
        self.app_port_frame_1 = None
        self.bd_frame_1 = None
        self.result_label = None
        self.message_label = None
        self.combobox1 = None
        self.applications = []
        self.process = None
        self.process_thread = None
        self.pid_proc = None
        self.pid_sub_proc = None
        self.global_dotnet_process_pid = None
        self.stop_signal = threading.Event()
        self.existing_settings = {}
        self.root = self
        self.style = ttk.Style()
        self.root.geometry("800x300+0+0")
        self.root.iconbitmap('icons/icon.ico')
        self.root.title(f"CRM Starter v{version_app}")
        self.load_static_content()
        self.create_gui()
        self.load_settings()
        self.after(500, self.delayed_check_for_updates)

    @basis_handle_errors("create_gui")
    def create_gui(self):
        self.root.minsize(800, 480)
        self.root.maxsize(800, 480)
        window_width = 800
        window_height = 480
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # --------------------------------------------------------------------------------------------------------------
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=(15, 15), pady=(0, 15), sticky="nsew")

        self.tab_view.add(nameTab1)
        self.tab_view.add(nameTab2)
        # --------------------------------------------------------------------------------------------------------------
        base_combo_box_frame = ctk.CTkFrame(self.tab_view.tab(nameTab1), corner_radius=0)
        base_combo_box_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        combo_box_frame = ctk.CTkFrame(base_combo_box_frame, corner_radius=0)
        combo_box_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.load_settings()
        values = [app['folder'] for app in self.applications]
        self.combobox1 = ctk.CTkComboBox(combo_box_frame, width=730, height=30, values=values, border_width=1,
                                         command=self.update_fields, font=font14, dropdown_font=font14)
        self.combobox1.grid(row=0, column=0, columnspan=1, padx=(15, 20), pady=(15, 15), sticky="ns")
        # --------------------------------------------------------------------------------------------------------------
        base_frame = ctk.CTkFrame(self.tab_view.tab(nameTab1))
        base_frame.grid(row=1, column=0, padx=(0, 0), pady=(0, 10), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        left_frame_entry = ctk.CTkFrame(base_frame, corner_radius=0)
        left_frame_entry.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        right_frame_btn = ctk.CTkFrame(base_frame, corner_radius=0)
        right_frame_btn.grid(row=0, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        base_btn_frame = ctk.CTkFrame(right_frame_btn, corner_radius=0)
        base_btn_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        btn_frame = ctk.CTkFrame(base_btn_frame, corner_radius=0)
        btn_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.button_stop = ctk.CTkButton(btn_frame,
                                         width=150, height=30,
                                         text="Остановить", command=self.stop_command)
        self.button_stop.grid(row=0, column=0, columnspan=1, padx=(20, 15), pady=(0, 15), sticky="n")

        self.button_start = ctk.CTkButton(btn_frame, text="Стартанём!",
                                          width=160, height=30,
                                          command=self.run_command)
        self.button_start.grid(row=0, column=1, columnspan=1, padx=(0, 0), pady=(0, 15), sticky="w")

        self.button_stop = ctk.CTkButton(btn_frame,
                                         width=325, height=30,
                                         text="Открыть приложение в браузере",
                                         command=self.start_app)
        self.button_stop.grid(row=1, column=0, columnspan=2, padx=(20, 0), pady=(0, 15), sticky="nw")
        # --------------------------------------------------------------------------------------------------------------
        message_frame = ctk.CTkFrame(base_btn_frame, corner_radius=0)
        message_frame.grid(row=1, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.message_label = ctk.CTkTextbox(message_frame, font=font14, width=330, height=200)
        self.message_label.grid(row=1, column=0, rowspan=3, columnspan=2, padx=(15, 0), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        btn_frame_2 = ctk.CTkFrame(base_btn_frame, corner_radius=0)
        btn_frame_2.grid(row=2, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.button_change = ctk.CTkButton(btn_frame_2, text="Изменить данные",
                                           width=150, height=30,
                                           command=self.change_settings)
        self.button_change.grid(row=0, column=0, columnspan=1, padx=(20, 0), pady=(15, 15), sticky="nsew")

        self.button_delete = ctk.CTkButton(btn_frame_2, text="Удалить настройку",
                                           width=160, height=30,
                                           command=self.delete_settings)

        self.button_delete.grid(row=0, column=1, columnspan=1, padx=(15, 15), pady=(15, 15), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.alias_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.alias_frame_1.grid(row=0, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.path_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.path_frame_1.grid(row=1, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")
        self.path_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.path_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.bd_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.bd_frame_1.grid(row=2, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.app_port_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.app_port_frame_1.grid(row=3, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.redis_port_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.redis_port_frame_1.grid(row=4, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        img = ctk.CTkImage(light_image=Image.open("icons/clean.ico"),
                           dark_image=Image.open("icons/clean.ico"),
                           size=(30, 30))

        self.button_change = ctk.CTkButton(left_frame_entry, image=img, text="", bg_color="transparent",
                                           width=5, height=5, corner_radius=0, border_width=0,
                                           border_spacing=0,
                                           command=self.redis_clear)
        self.button_change.grid(row=4, column=2, rowspan=1, padx=(0, 0), pady=(10, 0), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.pg_port_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.pg_port_frame_1.grid(row=5, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.dll_frame_1 = ctk.CTkEntry(left_frame_entry, width=260, height=30, font=font12, border_width=1)
        self.dll_frame_1.grid(row=6, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        label1 = ctk.CTkLabel(left_frame_entry, text="Aлиас:", anchor="w", font=font12)
        label1.grid(row=0, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label1 = ctk.CTkLabel(left_frame_entry, text="Путь:", anchor="w", font=font12)
        label1.grid(row=1, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label2 = ctk.CTkLabel(left_frame_entry, text="БД:", anchor="w", font=font12)
        label2.grid(row=2, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label3 = ctk.CTkLabel(left_frame_entry, text="Порт:", anchor="w", font=font12)
        label3.grid(row=3, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label4 = ctk.CTkLabel(left_frame_entry, text="Redis:", anchor="w", font=font12)
        label4.grid(row=4, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label5 = ctk.CTkLabel(left_frame_entry, text="pg порт:", anchor="w", font=font12)
        label5.grid(row=5, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")

        label6 = ctk.CTkLabel(left_frame_entry, text="dll:", anchor="w", font=font12)
        label6.grid(row=6, column=0, padx=(15, 0), pady=(15, 5), sticky="nsew")
        # frame2 -------------------------------------------------------------------------------------------------------
        frame2 = ctk.CTkFrame(self.tab_view.tab(nameTab2), corner_radius=5, width=800, height=480)
        frame2.grid(row=0, column=0, columnspan=4, padx=(0, 0), pady=(0, 0), sticky="nsew")

        base_frame_2 = ctk.CTkFrame(frame2, corner_radius=5, width=800, height=480)
        base_frame_2.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        settings_frame = ctk.CTkFrame(base_frame_2, corner_radius=5, width=800, height=480)
        settings_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        theme_frame = ctk.CTkFrame(base_frame_2, corner_radius=5, width=800, height=480)
        theme_frame.grid(row=0, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        label1 = ctk.CTkLabel(settings_frame, text="Aлиас:", anchor="e", font=font14)
        label1.grid(row=0, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label1 = ctk.CTkLabel(settings_frame, text="Путь:", anchor="e", font=font14)
        label1.grid(row=1, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label2 = ctk.CTkLabel(settings_frame, text="БД:", anchor="e", font=font14)
        label2.grid(row=2, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label3 = ctk.CTkLabel(settings_frame, text="Порт:", anchor="e", font=font14)
        label3.grid(row=3, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label4 = ctk.CTkLabel(settings_frame, text="Redis:", anchor="e", font=font14)
        label4.grid(row=4, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label5 = ctk.CTkLabel(settings_frame, text="pg порт:", anchor="e", font=font14)
        label5.grid(row=5, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")

        label6 = ctk.CTkLabel(settings_frame, text="dll:", anchor="e", font=font14)
        label6.grid(row=6, column=0, padx=(15, 50), pady=(15, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.alias_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.alias_frame_2.grid(row=0, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.path_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.path_frame_2.grid(row=1, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.bd_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.bd_frame_2.grid(row=2, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.app_port_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.app_port_frame_2.grid(row=3, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.redis_port_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.redis_port_frame_2.grid(row=4, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.pg_port_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.pg_port_frame_2.grid(row=5, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        self.dll_frame_2 = ctk.CTkEntry(settings_frame, font=font14, width=300, height=30)
        self.dll_frame_2.grid(row=6, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")

        button2 = ctk.CTkButton(settings_frame, text="Сохранить",
                                command=self.save_settings)
        button2.grid(row=7, column=1, padx=(15, 15), pady=(15, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        redis_frame_settings = ctk.CTkFrame(theme_frame, corner_radius=5, fg_color="transparent")
        redis_frame_settings.grid(row=0, column=0, padx=(15, 15), pady=(45, 15), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        host_app_label1 = ctk.CTkLabel(redis_frame_settings, text="Host app:", anchor="e", font=font14)
        host_app_label1.grid(row=0, column=0, padx=(0, 15), pady=(0, 35), sticky="n")

        host_app_entry = ctk.CTkEntry(redis_frame_settings, font=font14, textvariable=self.host_app)
        host_app_entry.grid(row=0, column=1, padx=(0, 15), pady=(0, 15), sticky="n")
        # --------------------------------------------------------------------------------------------------------------
        redis_host_label1 = ctk.CTkLabel(redis_frame_settings, text="Host redis:", anchor="e", font=font14)
        redis_host_label1.grid(row=1, column=0, padx=(0, 15), pady=(0, 35), sticky="n")

        redis_host_entry = ctk.CTkEntry(redis_frame_settings, font=font14, textvariable=self.redis_host_theme)
        redis_host_entry.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="n")
        # --------------------------------------------------------------------------------------------------------------
        redis_port_label1 = ctk.CTkLabel(redis_frame_settings, text="Port redis:", anchor="e", font=font14)
        redis_port_label1.grid(row=2, column=0, padx=(0, 15), pady=(0, 35), sticky="n")

        redis_port_entry = ctk.CTkEntry(redis_frame_settings, font=font14, textvariable=self.redis_port_theme)
        redis_port_entry.grid(row=2, column=1, padx=(0, 15), pady=(0, 0), sticky="n")
        # --------------------------------------------------------------------------------------------------------------
        button_redis = ctk.CTkButton(redis_frame_settings, text="Сохранить",
                                     command=self.save_redis_settings)
        button_redis.grid(row=2, column=1, padx=(0, 15), pady=(45, 30), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        default_theme_label1 = ctk.CTkLabel(redis_frame_settings, text="Цвет элементов:", anchor="e", font=font14)
        default_theme_label1.grid(row=3, column=0, padx=(0, 15), pady=(0, 35), sticky="n")

        self.default_theme_entry = ctk.CTkEntry(redis_frame_settings, font=font14, textvariable=self.default_theme)
        self.default_theme_entry.grid(row=3, column=1, padx=(0, 15), pady=(0, 15), sticky="n")
        self.default_theme.trace_add("write", self.check_text)
        # --------------------------------------------------------------------------------------------------------------
        theme_settings = ctk.CTkFrame(theme_frame, corner_radius=5, fg_color="transparent")
        theme_settings.grid(row=1, column=0, padx=(15, 15), pady=(5, 15), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.appearance_mode_option_menu = ctk.CTkOptionMenu(master=theme_settings, width=145, button_color="#4b4b4b",
                                                             values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)

        self.appearance_mode_option_menu.grid(row=0, column=0, padx=(130, 15), pady=(0, 15), sticky="w")

        self.appearance_mode_option_menu.set(self.theme.get())

    def check_text(self, *args):
        entered_text = self.default_theme.get()
        if entered_text.endswith("_theme"):
            b_theme = entered_text.replace("_theme", "")
            self.save_to_settings_one_attribute("default_theme", b_theme)
            ctk.set_default_color_theme(b_theme)
            self.message_restart()

    def message_restart(self):
        confirmation = CTkMessagebox(title="Информация",
                                     message=f"Для того, что бы изменение вступили в силу, требуется перезагрузка.\n\n",
                                     option_1="Перезагрузить", option_2="Нет", button_width=85, button_height=30,
                                     font=font14)
        response = confirmation.get()
        if response == "Перезагрузить":
            self.restart_app()
        else:
            self.set_attribute_from_settings_data("default_theme", self.default_theme_entry)

    @basis_handle_errors("load_settings")
    def load_static_content(self):
        try:
            global static_content
            with open('static_data.json', 'r', encoding='utf-8') as file:
                static_content = json.load(file)

        except FileNotFoundError:
            print(f"{self.set_static_content('file_not_exists_message')}")
        except Exception as e:
            print(f"{self.set_static_content('load_error_message')}: {e}")

    @basis_handle_errors("load_settings")
    def load_settings(self):
        try:
            with open('settings.json', 'r', encoding='utf-8') as settings_file:
                settings_data = json.load(settings_file)
                self.theme.set(settings_data.get('theme', "system"))
                self.default_theme.set(settings_data.get('default_theme', "green"))

                self.redis_host_theme.set(settings_data.get('redis_host', "127.0.0.1"))
                self.redis_port_theme.set(settings_data.get('redis_port', "6379"))
                self.host_app.set(settings_data.get('host_app', "localhost"))

                self.applications.extend(settings_data.get('applications', []))
                self.combobox1['values'] = [app['folder'] for app in self.applications]
                self.update_fields_data()
        except FileNotFoundError:
            print(f"{self.set_static_content('file_not_exists_message')}")
        except Exception as e:
            print(f"{self.set_static_content('load_error_message')}: {e}")
        finally:
            ctk.set_appearance_mode(self.theme.get())
            ctk.set_default_color_theme(self.default_theme.get())

    @basis_handle_errors("change_data")
    def change_settings(self):
        global path_delete

        alias_value, path_value, bd_value, app_port_value, redis_port_value, pg_port_value, dll_value = self.get_frame_values(
            self.alias_frame_1, self.path_frame_1, self.bd_frame_1, self.app_port_frame_1, self.redis_port_frame_1,
            self.pg_port_frame_1, self.dll_frame_1
        )

        try:
            with open('settings.json', 'r') as settings_file:
                existing_settings = json.load(settings_file)
        except FileNotFoundError:
            existing_settings = {"applications": []}
        except Exception as ex:
            self.handle_error_message(f"{self.set_static_content('load_error_message')}: {ex}")
            return

        existing_app = self.find_existing_app(existing_settings, path_value)
        new_app_data = {
            "alias": alias_value,
            "folder": path_value,
            "port": app_port_value,
            "db": bd_value,
            "redis": redis_port_value,
            "postgresql_port": pg_port_value,
            "dll": dll_value,
        }

        if existing_app:
            existing_app.update(new_app_data)
        else:
            existing_settings['applications'].append(new_app_data)

        try:
            with open('settings.json', 'w') as settings_file:
                json.dump(existing_settings, settings_file, indent=4)
            self.handle_success_message(self.set_static_content('success_message_changed'))
        except Exception as ex:
            self.handle_error_message(f"{self.set_static_content('load_error_message')}: {ex}")
        else:
            self.delete_settings(path_delete)
            self.update_data()

    @basis_handle_errors("save_settings")
    def save_settings(self):
        alias_value, path_value, bd_value, app_port_value, redis_port_value, pg_port_value, dll_value = self.get_frame_values(
            self.alias_frame_2, self.path_frame_2, self.bd_frame_2, self.app_port_frame_2, self.redis_port_frame_2,
            self.pg_port_frame_2, self.dll_frame_2
        )

        try:
            with open('settings.json', 'r') as settings_file:
                existing_settings = json.load(settings_file)
        except FileNotFoundError:
            existing_settings = {"applications": []}
        except Exception as ex:
            self.handle_error_message(f"{self.set_static_content('load_error_message')}: {ex}")
            return

        existing_app = self.is_exist_setting(path_value)
        new_app_data = {
            "alias": alias_value,
            "folder": path_value,
            "port": app_port_value,
            "db": bd_value,
            "redis": redis_port_value,
            "postgresql_port": pg_port_value,
            "dll": dll_value,
        }

        if existing_app:
            existing_app.update(new_app_data)
        else:
            existing_settings['applications'].append(new_app_data)

        try:
            with open('settings.json', 'w') as settings_file:
                json.dump(existing_settings, settings_file, indent=4)
            CTkMessagebox(title="Информация", message=self.set_static_content('success_message_save'))
            self.update_data()
            self.clear_fields()
        except Exception as ex:
            self.handle_error_message(f"{self.set_static_content('save_load_error_message')}: {ex}")

    def delete_settings(self, delete_path=None):
        path_to_delete = None
        path_to_delete = delete_path if delete_path else self.get_folder_path_and_dll(path_to_delete)
        self.existing_settings = {}
        try:
            with open('settings.json', 'r') as settings_file:
                self.existing_settings = json.load(settings_file)
        except FileNotFoundError:
            self.existing_settings = {"applications": []}
        except Exception as ex:
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, f"{self.set_static_content('load_error_message')}: {ex}")
            return

        existing_app = self.is_exist_setting(path_to_delete)
        if existing_app:
            self.existing_settings['applications'].remove(existing_app)
            self.applications = self.existing_settings.get("applications", [])
            try:
                with open('settings.json', 'w') as settings_file:
                    json.dump(self.existing_settings, settings_file, indent=4)
                self.message_label.delete('1.0', tk.END)
                self.message_label.insert(tk.END,
                                          f"{self.set_static_content('success_message_delete')}. ['{path_to_delete}']")
            except Exception as ex:
                self.message_label.delete('1.0', tk.END)
                self.message_label.insert(tk.END, f"{self.set_static_content('load_error_message')}: {ex}")
            finally:
                self.update_data()
        else:
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, f"{self.set_static_content('not_found')} ['{path_to_delete}']")

    def clear_fields(self):
        self.alias_frame_2.delete(0, tk.END)
        self.path_frame_2.delete(0, tk.END)
        self.bd_frame_2.delete(0, tk.END)
        self.app_port_frame_2.delete(0, tk.END)
        self.redis_port_frame_2.delete(0, tk.END)
        self.pg_port_frame_2.delete(0, tk.END)
        self.dll_frame_2.delete(0, tk.END)

    def update_combobox(self, is_fields_cleared=True):
        combobox_values = [app['folder'] for app in self.applications]
        self.combobox1.set("")
        self.combobox1['values'] = combobox_values

        if is_fields_cleared:
            self.alias_frame_1.delete(0, tk.END)
            self.path_frame_1.delete(0, tk.END)
            self.bd_frame_1.delete(0, tk.END)
            self.app_port_frame_1.delete(0, tk.END)
            self.redis_port_frame_1.delete(0, tk.END)
            self.pg_port_frame_1.delete(0, tk.END)
            self.dll_frame_1.delete(0, tk.END)

    @basis_handle_errors("update_fields")
    def update_fields(self, event):
        self.message_label.delete('1.0', tk.END)
        selected_folder = self.combobox1.get()

        # Обновление данных self.applications
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.applications = settings.get('applications', [])
        except FileNotFoundError:
            self.applications = []
        except Exception as ex:
            self.message_label.insert(tk.END, f"{self.set_static_content('load_error_message')}: {ex}")
            return

        # Обновление данных self.combobox1
        self.combobox1['values'] = [app['folder'] for app in self.applications]

        self.set_fields(selected_folder)

    @basis_handle_errors("update_fields")
    def update_fields_data(self):
        selected_folder = self.combobox1.get()
        self.set_fields(selected_folder)

    def set_fields(self, selected_folder):
        if selected_folder:
            selected_app = next((app for app in self.applications if app['folder'] == selected_folder), None)
            if selected_app:
                self.alias_frame_1.delete(0, tk.END)
                self.alias_frame_1.insert(0, selected_app['alias'])
                self.path_frame_1.delete(0, tk.END)
                self.path_frame_1.insert(0, selected_app['folder'])
                self.bd_frame_1.delete(0, tk.END)
                self.bd_frame_1.insert(0, selected_app['db'])
                self.app_port_frame_1.delete(0, tk.END)
                self.app_port_frame_1.insert(0, selected_app['port'])
                self.redis_port_frame_1.delete(0, tk.END)
                self.redis_port_frame_1.insert(0, str(selected_app['redis']))
                self.pg_port_frame_1.delete(0, tk.END)
                self.pg_port_frame_1.insert(0, str(selected_app['postgresql_port']))
                self.dll_frame_1.delete(0, tk.END)
                self.dll_frame_1.insert(0, selected_app['dll'])

    @basis_handle_errors("run_command")
    def run_command(self):
        current_directory = os.getcwd()
        try:
            selected_folder = self.combobox1.get()
            if selected_folder:
                selected_app = next((app for app in self.applications if app['folder'] == selected_folder), None)
                if selected_app:
                    dll_path = selected_app.get('dll', '')
                    if dll_path:
                        folder_path = selected_app['folder']
                        alias = selected_app['alias']

                        if self.is_tab_open(alias):
                            messagebox.showerror("Ошибка", f"Проект с таким именем {alias} уже открыт.")
                            return

                        create_tab = f"{alias}"
                        self.tab_view.add(create_tab)
                        new_frame = ctk.CTkFrame(self.tab_view.tab(create_tab), corner_radius=0)
                        new_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 0), pady=(0, 0))

                        self.canvas = ctk.CTkCanvas(new_frame, width=745, height=415,
                                                    borderwidth=0,
                                                    highlightthickness=0)
                        self.canvas.pack(side="left", fill="both", expand=True)

                        os.chdir(folder_path)

                        self.check_buttons_frame_inner = ctk.CTkFrame(self.canvas, width=745, height=415)
                        self.canvas.create_window((0, 0), window=self.check_buttons_frame_inner, anchor="nw")

                        self.scrollbar = ctk.CTkScrollbar(new_frame, orientation="vertical", corner_radius=0,
                                                          border_spacing=0,
                                                          command=self.canvas.yview)
                        console_output_text = ctk.CTkTextbox(self.check_buttons_frame_inner, wrap=tk.WORD, width=745,
                                                             height=415)
                        console_output_text.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 0), pady=(0, 0))
                        self.canvas.configure(yscrollcommand=self.scrollbar.set)
                        self.scrollbar.pack(side="right", fill="y")

                        new_frame.update_idletasks()
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        def run_process():
                            global process, pids
                            if dll_path == "BPMSoft.WebHost.dll":
                                command = f"{os.path.join(folder_path, 'BPMSoft.WebHost.exe')}"
                            else:
                                command = f"dotnet {dll_path}"

                            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                       text=True, startupinfo=startupinfo)
                            pids.append((process.pid, folder_path, alias))

                            monitor_thread = threading.Thread(target=self.monitor_processes_and_close_tabs)
                            monitor_thread.daemon = True
                            monitor_thread.start()

                            while True:
                                output_line = process.stdout.readline()
                                if not output_line:
                                    break
                                console_output_text.insert("0.0", output_line)

                                self.canvas.update_idletasks()
                                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

                        process_thread_run = threading.Thread(target=run_process)
                        process_thread_run.start()
                        subprocess.Popen(["powershell", "-noexit"], startupinfo=startupinfo)

        except Exception as e:
            Log.info(f"{self.set_static_content('run_command_error_message')}: {e}", "Exception")
        finally:
            os.chdir(current_directory)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    @staticmethod
    @basis_handle_errors("is_process_alive")
    def is_process_alive(pid):
        return psutil.pid_exists(pid)

    @staticmethod
    def find_last_dotnet_process():
        command = 'tasklist /FI "IMAGENAME eq dotnet.exe" /NH /FO CSV'
        output = subprocess.check_output(command, shell=True).decode('cp1251')

        dotnet_processes = []
        for line in output.splitlines():
            columns = line.split(',')
            if len(columns) >= 2:
                pid = int(columns[1].strip(' "'))
                dotnet_processes.append(pid)

        if len(dotnet_processes) > 0:
            last_dotnet_pid = max(dotnet_processes)
            return last_dotnet_pid
        else:
            return None

    @basis_handle_errors("monitor_processes_and_close_tabs")
    def monitor_processes_and_close_tabs(self):
        while True:
            for pid, folder_path, alias in pids:
                if not self.is_process_alive(pid):
                    if not self.is_monitoring_stop:
                        self.message_label.delete('1.0', tk.END)
                        self.message_label.insert(tk.END,
                                                  f"{self.set_static_content('process_stop_success_message')}: {pid}")
                    time.sleep(5)
                    last_dotnet_pid = self.find_last_dotnet_process()
                    if last_dotnet_pid and self.is_process_alive(last_dotnet_pid):
                        pid_exists = any(existing_pid == last_dotnet_pid for existing_pid, _, _ in pids)
                        if not pid_exists:
                            alias_exists = any(existing_alias == alias for _, _, existing_alias in pids)
                            if alias_exists:
                                index = next((index for index, (_, _, existing_alias) in enumerate(pids) if
                                              existing_alias == alias), None)
                                if index is not None:
                                    pids[index] = (last_dotnet_pid, folder_path, alias)
                    else:
                        self.close_tab_by_name(alias)
                        pids.remove((pid, folder_path, alias))

            time.sleep(5)

    @basis_handle_errors("on_ok")
    def on_ok(self, window, boxes):
        alias = None
        try:
            selected_pids = [pid for pid, var_box, folder_path, alias in boxes if var_box.get() == 1]

            for pid_proc_run, _, _, a in [(pid, var_box, folder_path, alias) for pid, var_box, folder_path, alias in
                                          boxes if var_box.get() == 1]:
                alias = a

                self.kill_process(alias, pid_proc_run)

            global pids
            pids = [(pid, folder_path, alias) for pid, folder_path, alias in pids if pid not in selected_pids]

            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END,
                                      f"{self.set_static_content('entry_was_successfully_deleted')}: {selected_pids}")
            window.destroy()
        except Exception as ex:
            self.message_label.insert(tk.END, f"{self.set_static_content('error_message')}: {ex}")
            self.close_tab_by_name(alias)
            window.destroy()

    def kill_process(self, alias, pid_proc_run):
        child_process = psutil.Process(pid_proc_run)
        child_process.terminate()
        self.close_tab_by_name(alias)

    @basis_handle_errors("close_tab_by_name")
    def close_tab_by_name(self, alias):
        try:
            fixed_tab_alias = alias
            self.tab_view.delete(fixed_tab_alias)
        except Exception as ex:
            Log.info(f"{self.set_static_content('error_closing_tab_message')}: {ex}", "Exception")
            pass

    @basis_handle_errors("stop_command")
    def stop_command(self):
        global pids
        if not pids:
            CTkMessagebox(title=f"{self.set_static_content('error_stop_process_message_title')}",
                          message=f"{self.set_static_content('error_start_process_message')}")
            return

        if len(pids) == 1:
            confirmation = CTkMessagebox(title="Информация",
                                         message=f"Процесс {pids[0][0]} [{pids[0][2]}] будет остановлен.\n\nВы уверены?\n\n",
                                         option_1="Остановить", option_2="Отменить", button_width=85, button_height=30,
                                         font=font14)
            response = confirmation.get()
            if response == "Остановить":
                self.kill_process(pids[0][2], pids[0][0])
                self.message_label.delete('1.0', tk.END)
                self.message_label.insert(tk.END,
                                          f"{self.set_static_content('process_stop_success_message')}: {pids[0][0]}")
                self.is_monitoring_stop = True

                pids = []
            return

        self.is_monitoring_stop = False

        window = ctk.CTkToplevel(self.root)

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        window.after(100, window.lift)
        window.title(f"{self.set_static_content('select_process_message')}")
        window.iconbitmap('icons/icon.ico')
        window.minsize(600, 400)
        window.maxsize(600, 400)
        window_width_window = 600
        window_height_window = 400

        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - window_width_window) // 2
        y = parent_y + (parent_height - window_height_window) // 2

        window.geometry(f"{window_width_window}x{window_height_window}+{x}+{y}")
        var_boxes = []
        for pid, folder_path, alias in pids:
            var_box = tk.IntVar()
            checkbox = ctk.CTkCheckBox(window, text=f"PID: {pid}, Путь: {folder_path}", variable=var_box)
            checkbox.pack(padx=0, pady=10)
            var_boxes.append((pid, var_box, folder_path, alias))

        window.update_idletasks()

        ok_button = ctk.CTkButton(window, text="OK", command=lambda: self.on_ok(window, var_boxes))
        ok_button.pack()

        window.mainloop()

    @staticmethod
    def on_entry_focus_in_message(event):
        global path_delete
        path_delete = None

    def on_entry_focus_in(self, event):
        path = None
        path = self.get_folder_path_and_dll(path)
        global path_delete
        path_delete = path

    @staticmethod
    def on_entry_focus_out():
        global path_delete
        path_delete = None

    def get_folder_path_and_dll(self, path_to_delete):
        selected_folder = self.combobox1.get()
        if selected_folder:
            selected_app = next((app for app in self.applications if app['folder'] == selected_folder), None)
            if selected_app:
                dll_path = selected_app.get('dll', '')
                if dll_path:
                    folder_path = selected_app['folder']
                    path_to_delete = folder_path
        return path_to_delete

    def is_tab_open(self, alias):
        try:
            tab_names = [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]
            return alias in tab_names
        except Exception as ex:
            Log.info(f"{self.set_static_content('error_check_tab_message')}: {ex}", "Exception")
            return False

    def is_exist_setting(self, path):
        return next(
            (app for app in self.existing_settings.get('applications', []) if app.get('folder') == path),
            None)

    @staticmethod
    def handle_error_message(error_message):
        CTkMessagebox(title="Ошибка", message=error_message)

    @staticmethod
    def handle_success_message(success_message):
        CTkMessagebox(title="Успех", message=success_message)

    @staticmethod
    def find_existing_app(existing_settings, path):
        for app in existing_settings.get('applications', []):
            if app.get('folder') == path:
                return app
        return None

    @staticmethod
    def set_static_content(content):
        return static_content[content]

    @staticmethod
    def get_frame_values(alias_frame, path_frame, bd_frame, app_port_frame, redis_port_frame, pg_port_frame,
                         dll_frame):
        alias_value = alias_frame.get()
        path_value = path_frame.get()
        bd_value = bd_frame.get()
        app_port_value = int(app_port_frame.get())
        redis_port_value = int(redis_port_frame.get())
        pg_port_value = int(pg_port_frame.get())
        dll_value = dll_frame.get()

        return alias_value, path_value, bd_value, app_port_value, redis_port_value, pg_port_value, dll_value

    def restart_app(self):
        python = sys.executable
        self.destroy()
        subprocess.call([python, "main.py"])

    def change_appearance_mode_event(self, new_appearance_mode):
        confirmation = CTkMessagebox(title="Информация",
                                     message=f"Для того, что бы изменение вступили в силу, требуется перезагрузка.\n\n",
                                     option_1="Перезагрузить", option_2="Нет", button_width=85, button_height=30,
                                     font=font14)
        response = confirmation.get()
        if response == "Перезагрузить":
            ctk.set_appearance_mode(new_appearance_mode)
            self.save_to_settings_one_attribute("theme", new_appearance_mode)
            self.restart_app()
        else:
            ctk.set_appearance_mode(new_appearance_mode)
            self.save_to_settings_one_attribute("theme", new_appearance_mode)

    @staticmethod
    def loading_file():
        """
        Открывает ссылку для загрузки файла.

        :return: None
        """

        webbrowser.open(updater.get_download_link())

    def check_for_updates(self):
        """
        Проверяет наличие обновлений приложения.

        :return: None
        """
        update_available, local_version = updater.check_update()

        if update_available:
            confirmation = CTkMessagebox(title="Обновление",
                                         message=f"Доступна новая версия программы [v{local_version}].\n\n",
                                         option_1="Скачать", option_2="Отменить", button_width=85, button_height=30,
                                         font=font14)
            response = confirmation.get()
            if response == "Скачать":
                self.loading_file()

    def delayed_check_for_updates(self):
        """
        Выполняет отложенную проверку наличия обновлений приложения.
        :return: None
        """
        self.check_for_updates()

    @staticmethod
    def save_to_settings_one_attribute(name_attribute, value):
        with open("settings.json", "r") as file:
            data = json.load(file)

        data[name_attribute] = value

        with open("settings.json", "w") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def set_attribute_from_settings_data(name_attribute, value):
        with open("settings.json", "r") as file:
            data = json.load(file)

            if not isinstance(value, tk.StringVar):
                value.delete(0, tk.END)
                value.insert(0, (data[name_attribute]))
            else:
                value.set((data[name_attribute]))

    def update_data(self):
        with open("settings.json", "r") as file:
            data = json.load(file)
            self.applications = []
            self.applications.extend(data.get('applications', []))
            self.combobox1.set("")
            self.combobox1.configure(values=[app['folder'] for app in self.applications])
            self.update_fields_data()
            self.update_idletasks()
            self.update()

    def redis_clear(self):
        """
        Выполняет чистка редиса
        :return: None
        """
        redis_db = self.redis_port_frame_1.get()
        r = redis.Redis(host=self.redis_host_theme.get(), port=int(self.redis_port_theme.get()), db=int(redis_db))

        # Очистка Redis базы данных
        r.flushdb()

        # Проверка, что база данных очищена
        keys = r.keys()
        if len(keys) == 0:
            CTkMessagebox(title="Успех", message=f"База данных редиса №{redis_db}, успешно очищена", font=font14)
        else:
            CTkMessagebox(title="Ошибка", message="Ошибка при очистке базы данных редиса...", font=font14)

    def save_redis_settings(self):
        self.save_to_settings_one_attribute('redis_host', self.redis_host_theme.get())
        self.save_to_settings_one_attribute('redis_port', int(self.redis_port_theme.get()))
        self.save_to_settings_one_attribute('host_app', self.host_app.get())
        CTkMessagebox(title="Успех", message=f"Данные редиса успешно сохранены!", font=font14)

    @basis_handle_errors("start_app")
    def start_app(self):
        url = f'https://{self.host_app.get()}:{self.app_port_frame_1.get()}'

        confirmation = CTkMessagebox(title="Запуск приложения",
                                     message=f"Открыть страницу {url} в браузере?",
                                     option_1="Открыть", option_2="Нет", option_3="Скопировать в буфер",
                                     font=font14)
        response = confirmation.get()

        if response == "Открыть":
            webbrowser.open(url, new=2, autoraise=True)
        elif response == "Скопировать в буфер":
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
        elif response == "Нет":
            return
