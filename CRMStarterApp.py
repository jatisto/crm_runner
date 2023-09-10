import json

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import psutil

from utility_function import basis_handle_errors, Log

process = None
pids = []
path_delete = None


@basis_handle_errors("CRMStarterApp")
class CRMStarterApp:
    def __init__(self, root):
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
        self.root = root
        self.style = ttk.Style()
        self.root.geometry("800x300+0+0")
        self.root.title("CRM Starter")
        self.create_gui()
        self.load_settings()

    @basis_handle_errors("load_settings")
    def load_settings(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings_data = json.load(settings_file)
                self.applications.extend(settings_data.get('applications', []))
                self.combobox1['values'] = [app['folder'] for app in self.applications]
        except FileNotFoundError:
            print("Файл settings.json не найден.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке настроек: {e}")

    @basis_handle_errors("change_data")
    def change_settings(self):
        alias_value = self.alias_frame_1.get()
        path_value = self.path_frame_1.get()
        bd_value = self.bd_frame_1.get()
        app_port_value = int(self.app_port_frame_1.get())
        redis_port_value = int(self.redis_port_frame_1.get())
        pg_port_value = int(self.pg_port_frame_1.get())
        dll_value = self.dll_frame_1.get()

        try:
            with open('settings.json', 'r') as settings_file:
                existing_settings = json.load(settings_file)
        except FileNotFoundError:
            existing_settings = {"applications": []}
        except Exception as ex:
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, f"Произошла ошибка при загрузке настроек: {ex}")
            return

        # Проверьте, существует ли настройка с таким же 'folder'
        existing_app = next(
            (app for app in existing_settings.get('applications', []) if app.get('folder') == path_value),
            None)

        if existing_app:
            # Если настройка существует, обновите ее значения
            existing_app.update({
                "alias": alias_value,
                "folder": path_value,
                "port": app_port_value,
                "db": bd_value,
                "redis": redis_port_value,
                "postgresql_port": pg_port_value,
                "dll": dll_value,
            })
        else:
            # Если настройка не существует, добавьте новую настройку в список
            existing_settings['applications'].append({
                "alias": alias_value,
                "folder": path_value,
                "port": app_port_value,
                "db": bd_value,
                "redis": redis_port_value,
                "postgresql_port": pg_port_value,
                "dll": dll_value,
            })

        # Сохраните обновленные настройки в файл
        try:
            with open('settings.json', 'w') as settings_file:
                json.dump(existing_settings, settings_file, indent=4)
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, "Настройки успешно сохранены.")
        except Exception as ex:
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, f"Произошла ошибка при сохранении настроек: {ex}")
        else:
            self.button_change.place_forget()
            self.update_combobox()

    @basis_handle_errors("save_settings")
    def save_settings(self):
        alias = self.alias_frame_2.get()
        path = self.path_frame_2.get()
        bd = self.bd_frame_2.get()
        app_port = int(self.app_port_frame_2.get())
        redis = int(self.redis_port_frame_2.get())
        port_pg = int(self.pg_port_frame_2.get())
        dll = self.dll_frame_2.get()

        try:
            with open('settings.json', 'r') as settings_file:
                self.existing_settings = json.load(settings_file)
        except FileNotFoundError:
            self.existing_settings = {"applications": []}
        except Exception as ex:
            self.message_label.insert(tk.END, f"Произошла ошибка при загрузке настроек: {ex}")
            return

        # Проверьте, существует ли настройка с таким же 'folder'
        existing_app = self.is_exist_setting(path)

        if existing_app:
            # Если настройка существует, обновите ее значения
            existing_app.update({
                "alias": alias,
                "folder": path,
                "port": app_port,
                "db": bd,
                "redis": redis,
                "postgresql_port": port_pg,
                "dll": dll,
            })
        else:
            # Если настройка не существует, добавьте новую настройку в список
            self.existing_settings['applications'].append({
                "alias": alias,
                "folder": path,
                "port": app_port,
                "db": bd,
                "redis": redis,
                "postgresql_port": port_pg,
                "dll": dll,
            })

        # Сохраните обновленные настройки в файл
        try:
            with open('settings.json', 'w') as settings_file:
                json.dump(self.existing_settings, settings_file, indent=4)
            self.message_label.insert(tk.END, "Настройки успешно сохранены.")
        except Exception as ex:
            self.message_label.insert(tk.END, f"Произошла ошибка при сохранении настроек: {ex}")
        finally:
            self.update_combobox()

    def is_exist_setting(self, path):
        return next(
            (app for app in self.existing_settings.get('applications', []) if app.get('folder') == path),
            None)

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
            self.message_label.insert(tk.END, f"Произошла ошибка при загрузке настроек: {ex}")
            return

        # Проверьте, существует ли настройка с таким же 'folder'
        existing_app = self.is_exist_setting(path_to_delete)

        if existing_app:
            # Если настройка существует, удалите ее из списка
            self.existing_settings['applications'].remove(existing_app)
            # Обновите self.applications
            self.applications = self.existing_settings.get("applications", [])
            # Сохраните обновленные настройки в файл
            try:
                with open('settings.json', 'w') as settings_file:
                    json.dump(self.existing_settings, settings_file, indent=4)
                self.message_label.delete('1.0', tk.END)
                self.message_label.insert(tk.END, f"Настройка '{path_to_delete}' успешно удалена.")
            except Exception as ex:
                self.message_label.delete('1.0', tk.END)
                self.message_label.insert(tk.END, f"Произошла ошибка при сохранении настроек: {ex}")
            finally:
                self.update_combobox()
        else:
            self.message_label.delete('1.0', tk.END)
            self.message_label.insert(tk.END, f"Настройка '{path_to_delete}' не найдена.")

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

    def update_combobox(self, is_fields_cleared=True):
        # Получите список значений для Combobox
        combobox_values = [app['folder'] for app in self.applications]

        # Удалите текущее значение Combobox
        self.combobox1.set("")

        # Установите новый список значений для Combobox
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
            self.message_label.insert(tk.END, f"Произошла ошибка при загрузке настроек: {ex}")
            return

        # Обновление данных self.combobox1
        self.combobox1['values'] = [app['folder'] for app in self.applications]

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

                        new_frame = ttk.Frame(self.notebook)
                        self.notebook.add(new_frame, text=f"{folder_path}")

                        os.chdir(folder_path)

                        console_output_text = tk.Text(new_frame, wrap=tk.WORD)
                        console_output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                        scrollbar = ttk.Scrollbar(new_frame, orient=tk.VERTICAL, command=console_output_text.yview)
                        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                        console_output_text.config(yscrollcommand=scrollbar.set)

                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        def run_process():
                            global process, pids
                            command = f"dotnet {dll_path}"

                            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                       text=True, startupinfo=startupinfo)
                            pids.append((process.pid, folder_path))

                            while True:
                                output_line = process.stdout.readline()
                                if not output_line:
                                    break
                                console_output_text.insert(tk.END, output_line)

                                self.canvas.update_idletasks()
                                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

                        process_thread_run = threading.Thread(target=run_process)
                        process_thread_run.start()
                        subprocess.Popen(["powershell", "-noexit"], startupinfo=startupinfo)
        except Exception as e:
            Log.info(f"Ошибка при запуске процесса: {e}", "Exception")
        finally:
            os.chdir(current_directory)

    @basis_handle_errors("on_ok")
    def on_ok(self, window, boxes):
        selected_pids = [pid for pid, var_box, folder_path in boxes if var_box.get() == 1]

        for pid_proc_run, _, folder_path in [(pid, var_box, folder_path) for pid, var_box, folder_path in boxes if
                                             var_box.get() == 1]:
            child_process = psutil.Process(pid_proc_run)
            child_process.terminate()
            self.close_tab_by_name(folder_path)

        global pids
        pids = [(pid, folder_path) for pid, folder_path in pids if pid not in selected_pids]

        self.result_label.insert(tk.END, f"Завершены процессы с PID: {selected_pids}")
        window.destroy()

    @basis_handle_errors("close_tab_by_name")
    def close_tab_by_name(self, tab_path):
        try:
            fixed_tab_path = tab_path
            Log.info(f"Закрываем вкладку: {fixed_tab_path}", "close_tab_by_name")

            index = None
            tab_names = [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]
            for i, name in enumerate(tab_names):
                if name == fixed_tab_path:
                    index = i
                    break

            if index is not None:
                self.notebook.forget(index)
        except Exception as ex:
            Log.info(f"Ошибка при закрытии вкладки: {ex}", "Exception")
            pass  # Обработка ошибки, если вкладка не найдена

    @basis_handle_errors("stop_command")
    def stop_command(self):
        if not pids:
            messagebox.showinfo("Нет активных процессов", "Нет запущенных процессов для завершения.")
            return

        window = tk.Toplevel(self.root)
        window.title("Выберите процессы для завершения")

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
        for pid, folder_path in pids:
            var_box = tk.IntVar()
            checkbox = tk.Checkbutton(window, text=f"PID: {pid}, Путь: {folder_path}", variable=var_box)
            checkbox.pack()
            var_boxes.append((pid, var_box, folder_path))

        window.update_idletasks()

        ok_button = tk.Button(window, text="OK", command=lambda: self.on_ok(window, var_boxes))
        ok_button.pack()

        window.mainloop()

    def on_entry_focus_in(self, event):
        self.button_delete.place_forget()
        self.button_change.place(width=120, height=25, x=648, y=300)
        path = None
        path = self.get_folder_path_and_dll(path)
        global path_delete
        path_delete = path

    def on_entry_focus_out(self, event):
        self.button_delete.place(width=120, height=25, x=648, y=300)
        global path_delete
        path_delete = None

    @basis_handle_errors("create_gui")
    def create_gui(self):
        self.root.minsize(800, 400)
        self.root.maxsize(800, 400)
        window_width = 800
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.canvas = tk.Canvas(self.root, width=780, height=400)
        self.canvas.place(x=10, y=10)

        self.canvas_scrollbar = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.canvas_scrollbar.place(x=10, y=375, width=780)

        self.canvas.configure(xscrollcommand=self.canvas_scrollbar.set)

        self.notebook = ttk.Notebook(self.canvas, width=780, height=350)
        self.notebook.place(x=10, y=10)

        self.canvas.create_window((0, 0), window=self.notebook, anchor='nw')
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        frame1 = ttk.Frame(self.notebook)
        self.notebook.add(frame1, text="Crm run")

        self.combobox1 = ttk.Combobox(frame1)
        self.combobox1.place(width=755, height=25, x=12, y=10)
        self.combobox1.bind('<<ComboboxSelected>>', self.update_fields)

        self.button_start = ttk.Button(frame1, text="Стартанём!", command=self.run_command)
        self.button_start.place(width=100, height=25, x=667, y=45)

        self.button_delete = ttk.Button(frame1, text="Удалить настройку", command=self.delete_settings)
        self.button_delete.place(width=120, height=25, x=648, y=300)

        self.button_change = ttk.Button(frame1, text="Изменить данные", command=self.change_settings)
        self.button_delete.place(width=120, height=25, x=648, y=300)

        self.button_stop = ttk.Button(frame1, text="Остановить процесс(ы)", command=self.stop_command)
        self.button_stop.place(width=150, height=25, x=505, y=45)

        self.result_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
        self.result_label.place(x=350, y=90)

        self.message_label = tk.Text(frame1, font=("Segoe UI", 10, "italic"), width=44, height=7)
        self.message_label.place(x=450, y=120)

        self.style.configure("Message.TLabel", foreground="green")  # Задайте нужный цвет, например, "green"

        self.alias_frame_1 = ttk.Entry(frame1)
        self.alias_frame_1.place(width=290, height=25, x=135, y=50)
        self.alias_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.alias_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.path_frame_1 = ttk.Entry(frame1)
        self.path_frame_1.place(width=290, height=25, x=135, y=90)
        self.path_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.path_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.bd_frame_1 = ttk.Entry(frame1)
        self.bd_frame_1.place(width=290, height=25, x=135, y=130)
        self.bd_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.bd_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.app_port_frame_1 = ttk.Entry(frame1)
        self.app_port_frame_1.place(width=291, height=25, x=135, y=170)
        self.app_port_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.app_port_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.redis_port_frame_1 = ttk.Entry(frame1)
        self.redis_port_frame_1.place(width=290, height=25, x=135, y=210)
        self.redis_port_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.redis_port_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.pg_port_frame_1 = ttk.Entry(frame1)
        self.pg_port_frame_1.place(width=290, height=25, x=135, y=250)
        self.pg_port_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.pg_port_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        self.dll_frame_1 = ttk.Entry(frame1)
        self.dll_frame_1.place(width=290, height=25, x=135, y=290)
        self.dll_frame_1.bind("<FocusIn>", self.on_entry_focus_in)
        self.dll_frame_1.bind("<FocusOut>", self.on_entry_focus_out)

        label1 = ttk.Label(frame1, text="Aлиас:", anchor="w", font="{Segoe UI} 10 {italic}")
        label1.place(width=120, height=25, x=10, y=50)

        label1 = ttk.Label(frame1, text="Путь:", anchor="w", font="{Segoe UI} 10 {italic}")
        label1.place(width=120, height=25, x=10, y=90)

        label2 = ttk.Label(frame1, text="БД:", anchor="w", font="{Segoe UI} 10 {italic}")
        label2.place(width=120, height=25, x=10, y=130)

        label3 = ttk.Label(frame1, text="Порт:", anchor="w", font="{Segoe UI} 10 {italic}")
        label3.place(width=120, height=25, x=10, y=170)

        label4 = ttk.Label(frame1, text="Redis:", anchor="w", font="{Segoe UI} 10 {italic}")
        label4.place(width=120, height=25, x=10, y=210)

        label5 = ttk.Label(frame1, text="pg порт:", anchor="w", font="{Segoe UI} 10 {italic}")
        label5.place(width=120, height=25, x=10, y=250)

        label6 = ttk.Label(frame1, text="dll:", anchor="w", font="{Segoe UI} 10 {italic}")
        label6.place(width=120, height=25, x=10, y=290)

        frame2 = ttk.Frame(self.notebook)
        self.notebook.add(frame2, text="setting")

        self.alias_frame_2 = ttk.Entry(frame2)
        self.alias_frame_2.place(width=290, height=25, x=230, y=10)

        self.path_frame_2 = ttk.Entry(frame2)
        self.path_frame_2.place(width=290, height=25, x=230, y=50)

        self.bd_frame_2 = ttk.Entry(frame2)
        self.bd_frame_2.place(width=290, height=25, x=230, y=90)

        self.app_port_frame_2 = ttk.Entry(frame2)
        self.app_port_frame_2.place(width=290, height=25, x=230, y=130)

        self.redis_port_frame_2 = ttk.Entry(frame2)
        self.redis_port_frame_2.place(width=290, height=25, x=230, y=170)

        self.pg_port_frame_2 = ttk.Entry(frame2)
        self.pg_port_frame_2.place(width=290, height=25, x=230, y=210)

        self.dll_frame_2 = ttk.Entry(frame2)
        self.dll_frame_2.place(width=290, height=25, x=230, y=250)

        button2 = ttk.Button(frame2, text="Сохранить", command=self.save_settings)
        button2.place(width=100, height=25, x=660, y=215)

        label1 = ttk.Label(frame2, text="Aлиас:", anchor="e", font="{Segoe UI} 10 {italic}")
        label1.place(width=120, height=25, x=95, y=10)

        label1 = ttk.Label(frame2, text="Путь:", anchor="e", font="{Segoe UI} 10 {italic}")
        label1.place(width=120, height=25, x=95, y=50)

        label2 = ttk.Label(frame2, text="БД:", anchor="e", font="{Segoe UI} 10 {italic}")
        label2.place(width=120, height=25, x=95, y=90)

        label3 = ttk.Label(frame2, text="Порт:", anchor="e", font="{Segoe UI} 10 {italic}")
        label3.place(width=120, height=25, x=95, y=130)

        label4 = ttk.Label(frame2, text="Redis:", anchor="e", font="{Segoe UI} 10 {italic}")
        label4.place(width=120, height=25, x=95, y=170)

        label5 = ttk.Label(frame2, text="pg порт:", anchor="e", font="{Segoe UI} 10 {italic}")
        label5.place(width=120, height=25, x=95, y=210)

        label6 = ttk.Label(frame2, text="dll:", anchor="e", font="{Segoe UI} 10 {italic}")
        label6.place(width=120, height=25, x=90, y=250)
