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
    
    elif command.startswith("job"):
        # Remove the 'job ' prefix
        job_command = command[len("job "):].strip()

        # Quick-add format: job add "role" "company" [status]
        if job_command.startswith("add "):
            # Split by quotes
            import re
            match = re.match(r'add\s+"([^"]+)"\s+"([^"]+)"(?:\s+(\w+))?', job_command)
            if match:
                role, company, status = match.groups()
                status = status or "todo"
                job_tracker.add_job(role, company, status)
                print(f'Added: {role} @ {company} (status={status})')
            else:
                print("Invalid quick-add format. Use: job add \"role\" \"company\" [status]")
        else:
            # Enter interactive mode for other commands
            job_tracker.interactive_mode()



    #if nothing else
    else:
        print("Sorry, I don’t understand that command.")


if __name__ == "__main__":
    print("Welcome to Shaco! Type 'exit' to quit.")
    exit_commands = {"exit", "quit", "bye", "close", "goodbye"}

    while True:
        user_input = input("> ").strip().lower()
        if user_input in exit_commands:
            print("Goodbye!")
            break
        handle_command(user_input)

