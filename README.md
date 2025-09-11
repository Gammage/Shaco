# Shaco - Personal AI Assistant

Shaco is a modular AI assistant built in Python. It’s designed to help you manage small tasks, reminders, calculations, and more. The goal of this project is to **learn Python, AI concepts, and project integration** while building something functional over time.

---

## **Project Structure**

Shaco/
│
├─ cheatsheet/
│ └─ python_cheatsheet.pdf # Quick Python reference
│
├─ projects/
│ ├─ math_helper.py # Math helper module
│ ├─ reminder_bot.py # Reminder bot module
│ └─ ... # Additional small projects
│
├─ shaco_core/
│ ├─ init.py
│ ├─ main.py # Main entry point for Shaco
│ ├─ command_parser.py # Handles user requests
│ └─ utils.py # Helper functions
│
├─ data/
│ ├─ user_notes.json
│ └─ logs/
│
├─ tests/
│ └─ test_math_helper.py
│
├─ README.md
└─ requirements.txt


---

## **Features**

- **Math Helper**: Basic calculator functions for addition, subtraction, multiplication, and division.
- **Reminder Bot**: Set reminders for tasks and notifications.
- **Expandable Modules**: Add your own Python scripts as new functionality.
- **Data Storage**: Store user notes and logs for Shaco’s reference.

---

## **Getting Started**

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/shaco.git
   cd shaco

2. Install dependencies (if any):
   pip install -r requirements.txt

3. Run assistant:
   python shaco_core/main.py

🛠 Future Plans

Add AI-powered responses

Integrate with local tools and APIs

Voice input and output

Task automation

🤝 Contributing

This is my personal project, but contributions and module ideas are welcome!
Add new scripts in projects/ and integrate them in shaco_core/main.py.
