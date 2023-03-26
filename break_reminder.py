import time
import threading
from time import sleep
import ctypes
from typing import Any

from plyer import notification
from datetime import datetime, timedelta

import tkinter as tk

# ==================== User-configurable settings ====================
# How long to work before a break? (in minutes)
work_duration_minutes = 45
# How long to be idle before it counts as a break (in minutes)
idle_time_threshold_minutes = 3
# How often to nudge the user if they're still working
overdue_nudge_frequency_minutes = 5


# ==================== Developer settings ====================
# Debug option: Use shorter times for debugging
debug_short_times = False
# Debug option: Print values of important variables to console
debug_variables = False
# How often to check whether user has been idle (mainly affects CPU usage)
check_interval_seconds = 10
# Use tkinter notifications?
enable_tkinter_notifications = True
# Use plyer notifications?
enable_plyer_notifications = True


# ==================== Code ====================
# Constants (internal)
if debug_short_times:
    # Override user-configurable constants with shorter times for debugging
    work_duration_minutes = 0.75
    idle_time_threshold_minutes = 0.5
    overdue_nudge_frequency_minutes = 0.25
work_duration = timedelta(minutes=work_duration_minutes)
idle_time_threshold = timedelta(minutes=idle_time_threshold_minutes)
overdue_nudge_frequency = timedelta(minutes=overdue_nudge_frequency_minutes)
tkinter_window_default_timeout = int(
    min(overdue_nudge_frequency, work_duration).total_seconds()) - 1

# Checks
if not enable_tkinter_notifications and not enable_plyer_notifications:
    raise Exception("At least one notification method must be enabled.")


def to_str(obj: datetime | timedelta) -> str:
    if isinstance(obj, datetime):
        return obj.strftime("%H:%M")
    elif isinstance(obj, timedelta):
        return format_duration(obj)
    else:
        raise TypeError(f"Unsupported type for to_str(): {type(obj)}")


def format_duration(duration: timedelta) -> str:
    seconds = duration.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


class LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]


def get_idle_time() -> timedelta:
    last_input_info = LastInputInfo()
    last_input_info.cbSize = ctypes.sizeof(last_input_info)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
    elapsed_time = (ctypes.windll.kernel32.GetTickCount() -
                    last_input_info.dwTime) / 1000
    return timedelta(seconds=elapsed_time)


class NotificationWindow:
    def __init__(self, title, message, timeout):
        self.title = title
        self.message = message
        self.timeout = timeout

    def close_window(self):
        self.window.destroy()

    def update_countdown(self):
        remaining_time = int(self.timeout - (time.time() - self.start_time))
        if remaining_time > 0:
            self.countdown_label.config(
                text=f"This message will disappear in {remaining_time} seconds")
            self.window.after(1000, self.update_countdown)
        else:
            self.close_window()

    def create_window(self):
        self.window = tk.Tk()
        self.window.title(self.title)
        self.window.geometry("300x200")
        self.window.attributes("-topmost", True)

        label = tk.Label(self.window, text=self.message, wraplength=280)
        label.pack(pady=10)

        self.countdown_label = tk.Label(self.window, text="")
        self.countdown_label.pack()

        button = tk.Button(self.window, text="OK", command=self.close_window)
        button.pack(pady=5)

        self.start_time = time.time()
        self.update_countdown()
        self.window.mainloop()


def show_custom_notification(title, message, timeout=tkinter_window_default_timeout):
    message = title + "\n\n" + message
    title = "Break Reminder"

    def create_window():
        notification = NotificationWindow(title, message, timeout)
        notification.create_window()

    window_thread = threading.Thread(target=create_window)
    window_thread.start()


def show_plyer_notification(title, message, timeout=10):
    notification.notify(
        title=title,
        message=message,
        app_name="Break Reminder",
        timeout=timeout,
    )


# Type hinting
notification: Any = notification


def main() -> None:
    # Show a notification when the program starts
    title = "Break Reminder is now running."
    message = "Time parameters chosen by you:\n" \
        f"Maximum work duration: {to_str(work_duration)}\n" \
        f"Minimum break duration: {to_str(idle_time_threshold)}\n" \
        f"When I forget, ping me every: {to_str(overdue_nudge_frequency)}"
    show_plyer_notification(title, message)
    show_custom_notification(title, message)

    start_time = datetime.now()
    overdue = False
    overdue_time = timedelta(seconds=0)
    last_nudge_time = datetime.now()
    while True:
        elapsed_time = datetime.now() - start_time

        # If user has been idle for at least idle_time_threshold_seconds, restart the work timer
        idle_time = get_idle_time()
        if idle_time.total_seconds() >= idle_time_threshold.total_seconds():
            start_time = datetime.now()
            overdue = False
            overdue_time = timedelta(seconds=0)

        # If the user has been active more than work_duration_minutes, show a notification and start overdue mode
        elif not overdue and (elapsed_time.total_seconds() >= work_duration.total_seconds()):
            title = f"Time for a {to_str(idle_time_threshold)} break!"
            message = f"You started working at {to_str(start_time)} and " \
                f"you've been active for {to_str(elapsed_time)}."
            show_plyer_notification(title, message)
            show_custom_notification(title, message)
            # Start overdue mode
            overdue = True
            last_nudge_time = datetime.now()

        elif overdue and last_nudge_time + overdue_nudge_frequency < datetime.now():
            # If the user has been active more than work_duration_minutes and already received a notification, show a nudging notification every overdue_nudge_frequency minutes
            overdue_time = elapsed_time - work_duration
            title = f"Break is {to_str(overdue_time)} overdue!"
            message = f"Why are you still working?\n"\
                f"You've been at it since {to_str(start_time)}.\n" \
                f"I'll nudge you every {to_str(overdue_nudge_frequency)} " \
                f"until you take a {to_str(idle_time_threshold)} break."
            show_plyer_notification(title, message)
            show_custom_notification(title, message)
            last_nudge_time = datetime.now()

        if debug_variables:
            # Print values to console for debugging: start_time, idle_time, elapsed_time, elapsed_time_since_last_break
            print()
            print(f"start_time: {to_str(start_time)}")
            print(f"idle_time: {to_str(idle_time)}")
            print(f"elapsed_time: {to_str(elapsed_time)}")
            print(f"overdue: {overdue}")
            print(f"overdue_time: {to_str(overdue_time)}")
            print("----------------------")

        sleep(check_interval_seconds)


if __name__ == "__main__":
    main()
