 # shaco_core/main.py
import sys
import os

# Add project root so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import job_tracker
from modules import math_helper
from modules import reminder_bot

def handle_command(command):
    """Decide which module to call based on user input."""
    
    #call the math helper
    if command.startswith("math"):
        # Example: "math add 5 3"
        _, operation, a, b = command.split()
        a, b = float(a), float(b)
        result = math_helper.calculate(operation, a, b)
        print(f"Result: {result}")

    #call the remind helper
    elif command.startswith("remind"):
        # Example: "remind buy milk 5"
        parts = command.split()
        reminder_text = " ".join(parts[1:-1])  # everything except the last word
        time_seconds = int(parts[-1])          # last word = seconds
        reminder_bot.add_reminder(reminder_text, time_seconds)
    
    #call the job tracker    
    elif command.startswith("job"):
    # Example: "job add" or "job list"
        job_command = command[len("job "):]
        job_tracker.interactive_mode(job_command)



    #if nothing else
    else:
        print("Sorry, I don’t understand that command.")


if __name__ == "__main__":
    print("Welcome to Shaco! Type 'exit' to quit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        handle_command(user_input)

