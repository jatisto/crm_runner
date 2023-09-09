import os
import datetime
import traceback

LOGS_DIR = "Logs"
datetime_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")
log_file = 'log_app.log'


def ensure_logs_dir():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)


def write_log(level, text_log, log_file) -> None:
    ensure_logs_dir()
    formatted_time = datetime_format
    log_entry = f"{formatted_time} [{os.getpid()}] {level} {text_log}"
    log_file_path = os.path.join(LOGS_DIR, log_file)
    with open(log_file_path, 'a', encoding='utf-8') as log:
        log.write(log_entry + '\n\n')  # Добавляем пустую строку после каждой записи


def handle_errors(log_file, text='', level="ERROR"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (Exception, KeyboardInterrupt) as exp:
                error_msg = f"{text}\n{str(exp)}\n{traceback.format_exc()}"
                write_log(level, error_msg, log_file)

        return wrapper

    return decorator


def basis_handle_errors(text='', level="ERROR"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (Exception, KeyboardInterrupt) as exp:
                error_msg = f"{text}\n{str(exp)}\n{traceback.format_exc()}"
                write_log(level, error_msg, 'root_error_log.log')

        return wrapper

    return decorator


class Log:
    @staticmethod
    def ensure_logs_dir():
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR, exist_ok=True)

    @staticmethod
    def write_log(level, text_log, log_file):
        Log.ensure_logs_dir()
        formatted_time = datetime_format
        log_entry = f"{formatted_time} [{os.getpid()}] {level} {text_log}"
        log_file_path = os.path.join(LOGS_DIR, log_file)
        with open(log_file_path, 'a', encoding='utf-8') as log:
            log.write(log_entry + '\n\n')

    @staticmethod
    def info(text, name_variable='unknown'):
        Log.write_log("INFO", f"[{name_variable}]: {text}", log_file)

    @staticmethod
    def error(text, name_variable='unknown'):
        Log.write_log("ERROR", f"[{name_variable}]: {text}", log_file)

    @staticmethod
    def warning(text, name_variable='unknown'):
        Log.write_log("WARNING", f"[{name_variable}]: {text}", log_file)

    @staticmethod
    def debug(text, name_variable='unknown'):
        Log.write_log("DEBUG", f"[{name_variable}]: {text}", log_file)
