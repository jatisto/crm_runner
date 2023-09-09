import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import psutil

from utility_function import basis_handle_errors, Log

applications = []
process = None
process_thread = None

pid_proc = None
pid_sub_proc = None
global dotnet_process_pid
pids = []
# selected_pids = []
# checkboxes = []
# var_boxes = []
stop_signal = threading.Event()

root = tk.Tk()
root.geometry("800x300+0+0")
root.title("CRM Starter")


def load_settings():
    try:
        with open('settings.json', 'r') as settings_file:
            settings_data = json.load(settings_file)
            applications.extend(settings_data.get('applications', []))
            combobox1['values'] = [app['folder'] for app in applications]
    except FileNotFoundError:
        print("Файл settings.json не найден.")
    except Exception as e:
        print(f"Произошла ошибка при загрузке настроек: {e}")


def save_settings():
    new_data = {
        "applications": [
            {
                "folder": entry1.get(),
                "port": int(entry2.get()),
                "db": entry3.get(),
                "redis": int(entry4.get()),
                "postgresql_port": int(entry5.get()),
                "dll": entry6.get(),
            }
        ]
    }

    try:
        with open('settings.json', 'w') as settings_file:
            json.dump(new_data, settings_file, indent=4)
    except Exception as ex:
        message_label.config(text=f"Произошла ошибка при сохранении настроек: {ex}")
        pass


def update_fields(event):
    selected_folder = combobox1.get()
    if selected_folder:
        selected_app = next((app for app in applications if app['folder'] == selected_folder), None)
        if selected_app:
            entry1.delete(0, tk.END)
            entry1.insert(0, selected_app['db'])
            entry2.delete(0, tk.END)
            entry2.insert(0, selected_app['port'])
            entry3.delete(0, tk.END)
            entry3.insert(0, str(selected_app['redis']))
            entry4.delete(0, tk.END)
            entry4.insert(0, str(selected_app['postgresql_port']))
            entry5.delete(0, tk.END)
            entry5.insert(0, selected_app['dll'])


@basis_handle_errors(text='run_command')
def run_command():
    current_directory = os.getcwd()
    try:
        selected_folder = combobox1.get()
        if selected_folder:
            selected_app = next((app for app in applications if app['folder'] == selected_folder), None)
            if selected_app:
                dll_path = selected_app.get('dll', '')
                if dll_path:
                    folder_path = selected_app['folder']

                    # Перейти в выбранную папку
                    os.chdir(folder_path)

                    # Очистить текстовое поле вывода
                    console_output_text.delete(1.0, tk.END)
                    current_directory_label.config(text=f"Текущая папка: {selected_folder}")
                    command_label.config(text=f"Команда: dotnet {dll_path}")

                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    @basis_handle_errors(text='run_command')
                    # Запустить процесс в отдельном потоке
                    def run_process():
                        global process, pids
                        command = f"dotnet {dll_path}"

                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                                   startupinfo=startupinfo)
                        pids.append((process.pid, folder_path))
                        # Остальной код остается без изменений
                        Log.info(f"Процесс запущен {process.pid}", "run_process")
                        pid_proc_label.config(text=f"Pid: {process.pid}")
                        global stop_signal
                        while not stop_signal.is_set():
                            output_line = process.stdout.readline()
                            if not output_line:
                                break
                            console_output_text.insert(tk.END, output_line)

                    process_thread_run = threading.Thread(target=run_process)
                    process_thread_run.start()
                    subprocess.Popen(["powershell", "-noexit"], startupinfo=startupinfo)
    except Exception as e:
        Log.info(f"Ошибка при запуске процесса: {e}", "Exception")
    finally:
        os.chdir(current_directory)


@basis_handle_errors(text='on_ok')
def on_ok(window, boxes):
    selected_pids = [pid for pid, var_box in boxes if var_box.get() == 1]

    for pid_proc_run in selected_pids:
        child_process = psutil.Process(pid_proc_run)
        child_process.terminate()

    global pids
    pids = [(pid, folder_path) for pid, folder_path in pids if pid not in selected_pids]

    result_label.config(text=f"Завершены дочерние процессы с PID: {selected_pids}")
    message_label.config(text="")
    console_output_text.insert(tk.END, f"Завершены дочерние процессы с PID: {selected_pids}")
    window.destroy()


@basis_handle_errors(text='stop_command')
def stop_command():
    # Проверка, есть ли активные процессы
    if not pids:
        messagebox.showinfo("Нет активных процессов", "Нет запущенных процессов для завершения.")
        return

    window = tk.Toplevel(root)
    window.title("Выберите процессы для завершения")
    window.minsize(600, 100)
    window.maxsize(600, 100)
    window_width_window = 600
    window_height_window = 100

    parent_x = root.winfo_x()
    parent_y = root.winfo_y()
    parent_width = root.winfo_width()
    parent_height = root.winfo_height()

    x = parent_x + (parent_width - window_width_window) // 2
    y = parent_y + (parent_height - window_height_window) // 2

    window.geometry(f"{window_width_window}x{window_height_window}+{x}+{y}")
    var_boxes = []
    for pid, folder_path in pids:
        var_box = tk.IntVar()
        checkbox = tk.Checkbutton(window, text=f"PID: {pid}, Путь: {folder_path}", variable=var_box)
        checkbox.pack()
        var_boxes.append((pid, var_box))

    window.update_idletasks()

    ok_button = tk.Button(window, text="OK", command=lambda: on_ok(window, var_boxes))
    ok_button.pack()

    window.mainloop()


# Добавьте эту функцию для выполнения других действий с выбранными PID
def do_something_with_selected_pids(selected_pids):
    if selected_pids:
        print("Выполняю действия с выбранными PID:", selected_pids)
    else:
        print("Нет выбранных PID")


def get_process_info_by_pid(pid):
    try:
        get_process = psutil.Process(pid)
        print(f"Имя процесса: {get_process.name()}")
        print(f"Командная строка: {get_process.cmdline()}")
        print(f"Статус процесса: {get_process.status()}")
        # Дополнительная информация о процессе доступна через атрибуты объекта process
    except psutil.NoSuchProcess as e:
        print(f"Процесс с PID {pid} не найден.")


root.minsize(800, 300)
root.maxsize(800, 300)
window_width = 800
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

notebook = ttk.Notebook(root, width=780, height=280)
notebook.place(x=10, y=10)

frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Crm run")

combobox1 = ttk.Combobox(frame1)
combobox1.place(width=756, height=25, x=10, y=10)
combobox1.bind('<<ComboboxSelected>>', update_fields)

button1 = ttk.Button(frame1, text="Run", command=run_command)
button1.place(width=100, height=25, x=665, y=45)

button_stop = ttk.Button(frame1, text="Stop Command", command=stop_command)
button_stop.place(width=100, height=25, x=555, y=45)

current_directory_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
current_directory_label.place(x=350, y=90)

command_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
command_label.place(x=350, y=120)

pid_proc_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
pid_proc_label.place(x=350, y=140)

result_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
result_label.place(x=350, y=160)

message_label = ttk.Label(frame1, text="", font=("Segoe UI", 10, "italic"))
message_label.place(x=350, y=180)

entry1 = ttk.Entry(frame1)
entry1.place(width=290, height=25, x=10, y=50)

entry2 = ttk.Entry(frame1)
entry2.place(width=291, height=25, x=10, y=210)

entry3 = ttk.Entry(frame1)
entry3.place(width=290, height=25, x=10, y=170)

entry4 = ttk.Entry(frame1)
entry4.place(width=290, height=25, x=10, y=130)

entry5 = ttk.Entry(frame1)
entry5.place(width=290, height=25, x=10, y=90)

frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="setting")

entry6 = ttk.Entry(frame2)
entry6.place(width=290, height=25, x=230, y=10)

entry7 = ttk.Entry(frame2)
entry7.place(width=290, height=25, x=230, y=170)

entry8 = ttk.Entry(frame2)
entry8.place(width=290, height=25, x=230, y=130)

entry9 = ttk.Entry(frame2)
entry9.place(width=290, height=25, x=230, y=90)

entry10 = ttk.Entry(frame2)
entry10.place(width=290, height=25, x=230, y=50)

button2 = ttk.Button(frame2, text="Сохранить", command=save_settings)
button2.place(width=100, height=25, x=660, y=215)

label1 = ttk.Label(frame2, text="Путь:", anchor="e", font="{Segoe UI} 10 {italic}")
label1.place(width=120, height=25, x=95, y=10)

label2 = ttk.Label(frame2, text="БД:", anchor="e", font="{Segoe UI} 10 {italic}")
label2.place(width=120, height=25, x=95, y=50)

label3 = ttk.Label(frame2, text="Порт:", anchor="e", font="{Segoe UI} 10 {italic}")
label3.place(width=120, height=25, x=95, y=90)

label4 = ttk.Label(frame2, text="Redis:", anchor="e", font="{Segoe UI} 10 {italic}")
label4.place(width=120, height=25, x=95, y=130)

label5 = ttk.Label(frame2, text="pg порт:", anchor="e", font="{Segoe UI} 10 {italic}")
label5.place(width=120, height=25, x=95, y=170)

entry11 = ttk.Entry(frame2)
entry11.place(width=290, height=25, x=230, y=210)

label6 = ttk.Label(frame2, text="dll:", anchor="e", font="{Segoe UI} 10 {italic}")
label6.place(width=120, height=25, x=90, y=210)

frame3 = ttk.Frame(notebook)
notebook.add(frame3, text="console log")

horizontal_paned_window = ttk.PanedWindow(frame3, orient=tk.HORIZONTAL)
horizontal_paned_window.place(width=765, height=245, x=5, y=5)

# Создайте текстовое поле для вывода консольного вывода
console_output_text = tk.Text(frame3, wrap=tk.WORD)
console_output_text.pack(fill=tk.BOTH, expand=True)

# Добавьте вертикальную полосу прокрутки для текстового поля
scrollbar = ttk.Scrollbar(frame3, orient=tk.VERTICAL, command=console_output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
console_output_text.config(yscrollcommand=scrollbar.set)

load_settings()
root.mainloop()
