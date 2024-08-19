import datetime
import traceback


def log_error(error: Exception) -> None:
    return
    time = str(datetime.datetime.now()).split(".")[0] # removed the milliseconds >w<
    with open("error_logs.txt", "a") as f:
        f.write(f"[{time}] {''.join(traceback.format_exception(error))}\n")


def retry_on_error(log: bool = True):
    def decorator(function):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    if log:
                        log_error(e)
        return wrapper
    return decorator
