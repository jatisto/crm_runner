import signal
import subprocess
import threading


class CommandRunner:
    def __init__(self):
        self.process = None
        self.stop_event = threading.Event()

    def run_command(self, selected_folder, dll_path):
        if selected_folder and dll_path:
            def run_process():
                command = f"dotnet {dll_path}"
                self.process = subprocess.Popen(["powershell", "-Command", command], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True)
                while not self.stop_event.is_set():
                    output_line = self.process.stdout.readline()
                    if not output_line:
                        break
                    # console_output_text.insert(tk.END, output_line)

                self.process.send_signal(signal.CTRL_C_EVENT)

            process_thread = threading.Thread(target=run_process)
            process_thread.start()

            subprocess.run(["powershell", "-Command", "Exit"])

    def stop_command(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
