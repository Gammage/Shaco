import time
import threading

def set_reminder(message, time_seconds):
    """Waits for time_seconds, then prints the reminder."""
    time.sleep(time_seconds)
    print(f"\n⏰ Reminder: {message}")

def add_reminder(message, time_seconds):
    """Start a reminder in the background (no input here)."""
    reminder_thread = threading.Thread(target=set_reminder, args=(message, time_seconds))
    reminder_thread.start()
    print(f"✅ Reminder set: '{message}' in {time_seconds} seconds")
