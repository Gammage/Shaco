🧠 Shaco – Personal AI Assistant

Shaco is a modular, privacy-first AI assistant built entirely in Python.
It’s designed to help automate small tasks, manage reminders, generate reports, and eventually integrate local AI reasoning — all offline and under your control.

This project is also a personal learning journey: a way to grow Python, automation, and AI integration skills by building something real over time.

## 📁 Project Structure
<pre>
Shaco/
├─ cheatsheet/
│   └─ python_cheatsheet.pdf
├─ projects/
│   ├─ math_helper.py
│   └─ reminder_bot.py
├─ shaco_core/
│   ├─ main.py
│   └─ utils.py
├─ data/
│   └─ user_notes.json
└─ requirements.txt
</pre>

✨ Current Features

🧮 Math Helper – Perform simple calculations directly from chat.

⏰ Reminder Bot – Set reminders and timed notifications.

🧩 Expandable Modules – Drop in new Python scripts to extend functionality.

🗂 Data Storage – Store user data and logs locally for future recall.

📊 CSV → PDF Report Generator – (In development) Automatically turn data into professional reports.

🧠 Local LLM Integration (Optional)

Shaco is built to integrate seamlessly with a local language model backend for reasoning and conversation.
This allows all AI interactions to run completely offline, keeping your data private and under your control.

🔧 How It Works

The /Llm folder (ignored in Git) contains your local model setup.

It connects to text-generation-webui
, an open-source interface for running models like Mistral 7B or LLaMA locally.

Shaco communicates with that backend through a simple local API (http://127.0.0.1:5000/api/v1/generate).

⚠️ The /Llm directory and model files are not included in this repository due to size and licensing restrictions.
If you’d like to run your own local model, see setup instructions in the text-generation-webui repository
.

🚀 Getting Started

Clone this repository:

git clone https://github.com/yourusername/shaco.git
cd shaco


Install dependencies:

pip install -r requirements.txt


Run Shaco:

python shaco_core/main.py

🧭 Roadmap

🤖 Integrate AI-powered responses (local and optional)

🧩 Build full RAG memory system (document and context recall)

🔊 Add voice input/output

⚙️ Expand automation capabilities

🧠 Fine-tune a local LoRA model for personality & reasoning

🤝 Contributing

This is an open personal project, but contributions and ideas are welcome!
You can:

Add new modules under projects/

Suggest improvements via issues or pull requests

Help test new automation or RAG features

📜 License

MIT License — free to modify and use locally.

💬 Contact

Questions, collaboration ideas, or feedback?

Open an issue on GitHub

Or connect via LinkedIn
 (add your link here)
