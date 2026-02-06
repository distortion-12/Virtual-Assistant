# ZENITH - Intelligent Agent-Based AI Assistant

> A production-ready, modular Python AI assistant framework with skill-based architecture, task planning, and agent-based orchestration

![Status](https://img.shields.io/badge/status-production%20ready-green)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Overview

ZENITH is an intelligent AI assistant system that understands natural language requests, breaks them into executable tasks, and coordinates modular skills to provide responses. It's designed with enterprise-grade architecture while remaining simple to extend and customize.

### Key Capabilities

- **Natural Language Understanding** - Parse complex, multi-step requests
- **Task Planning** - Break requests into prioritized, sequential tasks
- **Skill-Based Execution** - Modular, reusable skills for different domains
- **Agent Orchestration** - Intelligent coordination and result compilation
- **Multiple Interfaces** - Text, voice (speech recognition), and GUI (Tkinter)
- **Extensible Architecture** - Add new skills in just 3 steps
- **Production Ready** - Error handling, logging, configuration management

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd AI

# Install dependencies
pip install -r requirements.txt
```

### First Run (GUI is default)

```bash
# Launch ZENITH GUI
python executor.py
```

### First Voice Command (Wake Word)

```bash
python executor.py
# Say the wake word, then your command
# Example: "jarvis" → "what is python"
```

## 📋 What You Can Do

### Time & Date
```
"What's the time?"
"What's today's date?"
"Tell me the current date"
```

### Open Applications
```
"Open notepad"
"Launch calculator"
"Open browser"
```

### Search & Web
```
"Search Python tutorials"
"Open YouTube"
"Open Google"
```

### System Information
```
"System status"
"CPU usage"
"Memory information"
```

### File Operations
```
"Create file test.txt"
"Create folder my_folder"
"Take screenshot"
```

### Knowledge & Q&A
```
"Who is Albert Einstein?"
"What is machine learning?"
"Tell me about Python"
```

### Multi-Step Commands
```
"Open notepad and search Python"
"Create file and then open calculator"
"Get weather and tell me the time"
```

## 📚 Documentation

This project includes core documentation:

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Quick start and overview | Everyone |
| [USER_GUIDE.md](USER_GUIDE.md) | Full usage guide | Users & developers |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              User Interfaces                    │
│  (Text Mode | Voice Mode | GUI with Tkinter)   │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         ZenithAgent (Orchestrator)             │
│  • Plans requests into tasks                    │
│  • Manages execution flow                       │
│  • Compiles results                             │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ↓               ↓
┌──────────────────┐  ┌──────────────────┐
│  TaskPlanner     │  │  TaskExecutor    │
│  • Parses input  │  │  • Routes tasks  │
│  • Creates tasks │  │  • Executes      │
└──────────────────┘  └────────┬─────────┘
                               │
                        ┌──────┴──────┐
                        ↓             ↓
                   ┌─────────────────────────┐
                   │    9 Modular Skills     │
                   ├─────────────────────────┤
                   │ • Time/Date             │
                   │ • Applications          │
                   │ • System Info           │
                   │ • Web Search            │
                   │ • Files                 │
                   │ • Weather               │
                   │ • Knowledge Q&A         │
                   │ • Input                 │
                   │ • Messages              │
                   └─────────────────────────┘
```

## 📁 Project Structure

```
zenith/
├── README.md                    # Main documentation (this file)
├── USER_GUIDE.md               # Full usage guide
├── requirements.txt             # Python dependencies
├── zenith_config.json          # Local configuration (ignored)
├── zenith_config.example.json  # Safe example config
│
├── executor.py                  # ⭐ Main entry point
├── zenith.py                    # Core library (I/O, utilities)
├── zenith_ui.py                 # GUI interface (Tkinter)
│
├── skills/                      # 🛠️ Modular Skills (9 skills)
│   ├── __init__.py
│   ├── base_skill.py            # Abstract base class
│   ├── time_date.py             # ⏰ Time & Date
│   ├── applications.py          # 📱 Open applications
│   ├── system.py                # 💻 System information
│   ├── web.py                   # 🌐 Web search
│   ├── files.py                 # 📁 File operations
│   ├── weather.py               # 🌦️ Weather info
│   ├── knowledge.py             # 🧠 Q&A knowledge
│   ├── input.py                 # ⌨️ Input prompts
│   └── messages.py              # 💬 WhatsApp messaging
│
├── tasks/                       # 📋 Task Management System
│   ├── __init__.py
│   ├── hosted_intent.py          # Hosted intent routing
│   ├── task_manager.py          # Task & queue management
│   ├── task_executor.py         # Task execution
│   └── task_planner.py          # Request parsing
│
├── agents/                      # 🧠 Agent System
│   ├── __init__.py
│   └── zenith_agent.py          # Main agent orchestrator

```

## 🎓 Getting Started Tips

1. Start the GUI: `python executor.py`
2. Say the wake word and a simple command (time/date)
3. Try a multi-step command (open an app + search)
4. Review [USER_GUIDE.md](USER_GUIDE.md) for detailed usage

## 🛠️ Creating Your First Skill

### 3-Step Process

**Step 1: Create the skill file**
```python
# skills/greeting.py
from .base_skill import BaseSkill

class GreetingSkill(BaseSkill):
    def can_handle(self, command: str) -> bool:
        keywords = ["hello", "hi", "hey", "greet"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str) -> str:
        hour = int(time.strftime("%H"))
        if hour < 12:
            greeting = "Good morning!"
        elif hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        self.speak(greeting)
        return greeting
```

**Step 2: Register in executor.py**
```python
from skills.greeting import GreetingSkill

# In ZenithExecutor._register_skills():
executor.register_skill(GreetingSkill(self.jarvis))
```

**Step 3: Use it**
```
You: "Hello ZENITH"
ZENITH: "Good afternoon!"
```

For a complete walkthrough, follow the steps above and inspect existing skills.

## ⚙️ Configuration

Copy the example config and edit your local file:

```bash
copy zenith_config.example.json zenith_config.json
```

Then edit `zenith_config.json`:

```json
{
    "wake_word": "zenith",
    "voice_rate": 150,
    "voice_volume": 0.9,
    "weather_api_key": "",
    "user_name": "Sir",
    "theme": "default",
    "ai_intent_enabled": true,
    "use_agent_in_gui": true,
    "hf_api_token": "",
    "hf_model": "facebook/bart-large-mnli",
    "hf_min_score": 0.55,
    "picovoice_access_key": ""
}
```

### Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| wake_word | string | "zenith" | Activation word for voice mode |
| voice_rate | int | 150 | Speech rate (words per minute) |
| voice_volume | float | 0.9 | Speaker volume (0.0-1.0) |
| weather_api_key | string | "" | OpenWeatherMap API key |
| user_name | string | "Sir" | Personalized greeting name |
| theme | string | "default" | UI theme name |
| ai_intent_enabled | bool | true | Enable hosted intent routing |
| use_agent_in_gui | bool | true | Use agent pipeline in GUI |
| hf_api_token | string | "" | Hugging Face API token |
| hf_model | string | "facebook/bart-large-mnli" | Hosted intent model |
| hf_min_score | float | 0.55 | Minimum intent confidence |
| picovoice_access_key | string | "" | Porcupine wake word access key |
| google_api_key | string | "" | Google Generative Language API key |
| hf_code_model | string | "gpt2" | Hosted code model |

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

```
pyttsx3==2.90          # Text-to-speech
SpeechRecognition==3.10.0  # Speech recognition
pyaudio==0.2.14        # Microphone input
pvporcupine>=3.0.0     # Wake word detection (optional)
requests==2.31.0       # HTTP requests
psutil==5.9.5          # System info
pyautogui==0.9.54      # UI automation (optional)
Pillow==10.3.0         # Image processing (optional)
```

Optional dependencies are already listed in `requirements.txt`.

Install all:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

```bash
python executor.py
```

**Features:**
- Wake word detection (default: from `zenith_config.json`)
- Voice control + in‑UI text mode switch
- Activity log with timestamps
- Real-time status updates

## ✅ Quick Check

Run the app and verify wake word + voice works:

```bash
python executor.py
```

## 📦 Build Windows EXE

Install PyInstaller once:

```bash
pip install pyinstaller
```

Clean rebuild using the spec (recommended):

```bash
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Output is created in `dist\Zenith\Zenith.exe`.

Notes:
- Porcupine wake word requires `PICOVOICE_ACCESS_KEY` at runtime.
- If you change dependencies, rebuild the EXE.

## 🧠 System Features

### Intelligent Planning
- Parses complex requests with conjunctions ("and", "then")
- Breaks into prioritized tasks
- Handles multi-step commands
- Smart task merging

### Task Management
- FIFO queue with priority support
- Status tracking (PENDING → RUNNING → COMPLETED)
- Error recovery and retries
- Execution history

### Skill System
- 7 pre-built skills
- Extensible base class
- Independent skill execution
- Reusable across projects

### Agent Orchestration
- Request → Planning → Execution → Response
- State tracking (IDLE → THINKING → EXECUTING → COMPLETED)
- Logging and debugging
- Result compilation

## 🔍 Example Commands & Outputs

### Example 1: Simple Command
```
Input: "What's the time?"

Processing:
  1. Plan: 1 task (Get time)
  2. Execute: TimeAndDateSkill.execute()
  3. Result: "The current time is 2:30 PM"

Output: "The current time is 2:30 PM"
```

### Example 2: Multi-Step Command
```
Input: "Open notepad and search Python"

Processing:
  1. Plan: 2 tasks
     - Open notepad
     - Search Python
  2. Execute both tasks
  3. Result: Completed 2 tasks

Output:
  ✓ Opened notepad
  ✓ Searching for Python
```

### Example 3: Knowledge Query
```
Input: "Who is Albert Einstein?"

Processing:
  1. Plan: 1 task (Knowledge search)
  2. Execute: KnowledgeSkill searches Wikipedia
  3. Result: Retrieved biography

Output: "Albert Einstein was a theoretical 
physicist who developed the theory of 
relativity..."
```

## 🐛 Troubleshooting

### Microphone not working
```bash
# Test in Text Mode first
python executor.py
# Select: 2
```

### Module import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Skills not responding
1. Check `executor.py` skill registration
2. Verify skill keywords match command
3. Check error logs for exceptions
4. Run verification: `python verify_system.py`

### GUI not launching
```bash
# Ensure Tkinter is installed
# Windows: pip install tk
# macOS: Install via Homebrew
# Linux: sudo apt-get install python3-tk
```

## 🎯 Use Cases

### Personal Assistant
- Schedule management
- Reminders
- Information lookup
- Task automation

### Learning & Education
- Study AI agent systems
- Learn Python patterns
- Understand task planning
- Explore modular architecture

### Business Applications
- Customer service bot
- System monitoring
- Workflow automation
- Knowledge base interaction

### Research & Experimentation
- NLP experimentation
- Task planning research
- Agent behavior study
- Skill evaluation

## 🤝 Contributing

To contribute improvements:

1. Create a custom skill (see [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md))
2. Test thoroughly
3. Document your skill
4. Submit for integration

## 📄 License

This project is open source and available under the MIT License.


## 💡 Tips & Tricks

### Speed Up Text Input
Use command aliases:
- "time" instead of "What's the time?"
- "search Python" instead of "Search for Python tutorials"

### Batch Operations
Use conjunctions for multi-step commands:
```
"Open notepad and calculator then search Python"
```

### Voice Mode Tips
- Speak clearly and naturally
- Use complete sentences for complex requests
- Wait for ZENITH to finish speaking before next command
- Check microphone permissions in system settings

### Custom Configuration
Edit `zenith_config.json` to customize behavior:
- Faster/slower speech
- Different wake word
- Language preferences
- API keys for weather

## 🚀 Getting Help

1. **System issues?** → Reinstall dependencies: `pip install -r requirements.txt`

---

## 🎉 Ready to Start?

```bash
# Launch ZENITH
python executor.py

# Select mode 2 for Text Mode (easiest start)
# Try: "What's the time?"
```

**Enjoy using ZENITH!** 🚀

---

**Last Updated:** February 4, 2026
**Version:** 2.0 (Agent-based architecture)
**Status:** Production Ready ✓
