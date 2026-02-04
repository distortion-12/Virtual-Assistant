# JARVIS - Intelligent Agent-Based AI Assistant

> A production-ready, modular Python AI assistant framework with skill-based architecture, task planning, and agent-based orchestration

![Status](https://img.shields.io/badge/status-production%20ready-green)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Overview

JARVIS is an intelligent AI assistant system that understands natural language requests, breaks them into executable tasks, and coordinates modular skills to provide responses. It's designed with enterprise-grade architecture while remaining simple to extend and customize.

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

### First Run

```bash
# Launch JARVIS
python executor.py

# Select mode: 2 (Text Mode is easiest to start)
# Try a command: "What's the time?"
```

### First Voice Command

```bash
python executor.py
# Select mode: 1 (Voice Mode)
# Say: "What is Python?"
```

### First GUI Session

```bash
python jarvis_ui.py
# Click "LISTEN" or "TEXT INPUT"
# Interact with the interface
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
│         JarvisAgent (Orchestrator)              │
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
                   │    7 Modular Skills     │
                   ├─────────────────────────┤
                   │ • Time/Date             │
                   │ • Applications          │
                   │ • System Info           │
                   │ • Web Search            │
                   │ • Files                 │
                   │ • Weather               │
                   │ • Knowledge Q&A         │
                   └─────────────────────────┘
```

## 📁 Project Structure

```
jarvis/
├── README.md                    # Main documentation (this file)
├── USER_GUIDE.md               # Full usage guide
├── requirements.txt             # Python dependencies
├── jarvis_config.json          # Local configuration (ignored)
├── jarvis_config.example.json  # Safe example config
│
├── executor.py                  # ⭐ Main entry point
├── jarvis.py                    # Core library (I/O, utilities)
├── jarvis_ui.py                 # GUI interface (Tkinter)
│
├── skills/                      # 🛠️ Modular Skills (7 skills)
│   ├── __init__.py
│   ├── base_skill.py            # Abstract base class
│   ├── time_date.py             # ⏰ Time & Date
│   ├── applications.py          # 📱 Open applications
│   ├── system.py                # 💻 System information
│   ├── web.py                   # 🌐 Web search
│   ├── files.py                 # 📁 File operations
│   ├── weather.py               # 🌦️ Weather info
│   └── knowledge.py             # 🧠 Q&A knowledge
│
├── tasks/                       # 📋 Task Management System
│   ├── __init__.py
│   ├── task_manager.py          # Task & queue management
│   ├── task_executor.py         # Task execution
│   └── task_planner.py          # Request parsing
│
├── agents/                      # 🧠 Agent System
│   ├── __init__.py
│   └── jarvis_agent.py          # Main agent orchestrator
└── client/                      # 🌐 Optional web UI (React + Vite)
```

## 🎓 Learning Paths

### Beginner (15 minutes)
1. Read this README.md
2. Run: `python executor.py` (mode 2 - Text)
3. Try 5 example commands above
4. Read [QUICKSTART.md](QUICKSTART.md)

### Intermediate (1 hour)
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - System Design section
2. Study `executor.py` code
3. Explore one skill file (`skills/time_date.py`)
4. Try voice mode: `python executor.py` (mode 1)
5. Try GUI: `python jarvis_ui.py`

### Advanced (2 hours)
1. Read [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)
2. Create a custom skill (follow 3-step guide)
3. Register skill and test
4. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Extension section

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

# In JarvisExecutor._register_skills():
executor.register_skill(GreetingSkill(self.jarvis))
```

**Step 3: Use it**
```
You: "Hello JARVIS"
JARVIS: "Good afternoon!"
```

For complete guide, see [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)

## ⚙️ Configuration

Copy the example config and edit your local file:

```bash
copy jarvis_config.example.json jarvis_config.json
```

Then edit `jarvis_config.json`:

```json
{
    "wake_word": "jarvis",
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
| wake_word | string | "jarvis" | Activation word for voice mode |
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
pyttsx3>=2.90          # Text-to-speech
SpeechRecognition>=3.10.0  # Speech recognition
requests>=2.28.0       # HTTP requests
psutil>=5.9.0          # System info
Pillow>=9.0.0          # Image processing (for GUI)
```

Optional dependencies:
- `PvPorcupine` - For advanced wake word detection
- `python-dotenv` - For environment variables

Install all:
```bash
pip install -r requirements.txt
```

## 🎮 Usage Modes

### Mode 1: Voice Mode (Speech Recognition)
```bash
python executor.py
# Select: 1
# Speak your commands naturally
```

**Requires:** Microphone and audio input
**Best for:** Hands-free operation

### Mode 2: Text Mode (Keyboard Input)
```bash
python executor.py
# Select: 2
# Type your commands
```

**Requires:** Keyboard only
**Best for:** Development and testing

### Mode 3: GUI Mode (Visual Interface)
```bash
python jarvis_ui.py
```

**Features:**
- Sci‑fi HUD theme with animated core panel
- Wake word detection
- Manual listen and text input
- Activity log with timestamps
- Real-time status updates

**Best for:** User-friendly interaction

## ✅ Quick Check

Run the app and verify voice/text works:

```bash
python executor.py
```

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
# Verify system
python verify_system.py

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

## 📊 System Statistics

- **Total Code Files**: 21
- **Lines of Code**: 2000+
- **Documentation**: 13 files, 5000+ lines
- **Skills**: 7 built-in
- **Interfaces**: 3 (Text, Voice, GUI)
- **Architecture Patterns**: 5 (MVC, Strategy, Factory, Agent, Task Queue)

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
- Wait for JARVIS to finish speaking before next command
- Check microphone permissions in system settings

### Custom Configuration
Edit `jarvis_config.json` to customize behavior:
- Faster/slower speech
- Different wake word
- Language preferences
- API keys for weather

## 🚀 Getting Help

1. **System issues?** → Reinstall dependencies: `pip install -r requirements.txt`

---

## 🎉 Ready to Start?

```bash
# Launch JARVIS
python executor.py

# Select mode 2 for Text Mode (easiest start)
# Try: "What's the time?"
```

**Enjoy using JARVIS!** 🚀

---

**Last Updated:** February 4, 2026
**Version:** 2.0 (Agent-based architecture)
**Status:** Production Ready ✓
