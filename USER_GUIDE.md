# JARVIS User Guide (Complete)

> A complete, end-to-end guide to using JARVIS, including skills, tasks, modes, configuration, troubleshooting, and help.

## 📌 Table of Contents

1. Overview
2. Quick Start
3. Usage Modes
4. Skills (What Each Skill Can Do)
5. Tasks (What Tasks Can Be Performed)
6. How Skills Are Used (Skill Routing)
7. Commands and Examples
8. Configuration
9. Help & Troubleshooting
10. FAQ
11. Advanced Tips

---

## 1) Overview

JARVIS is a modular, agent-based AI assistant. It understands requests, plans tasks, and executes them through specialized skills. It works in three modes: voice, text, and GUI.

Key parts:
- **Agent Orchestrator**: Coordinates everything
- **Task Planner**: Breaks requests into tasks
- **Task Executor**: Executes tasks using skills
- **Skills**: Modular capability files for specific domains

---

## 2) Quick Start

### Install dependencies
```
pip install -r requirements.txt
```

### Run in Text Mode (easiest start)
```
python executor.py
# Select mode: 2
```

### Run in Voice Mode
```
python executor.py
# Select mode: 1
```

### Run in GUI Mode
```
python jarvis_ui.py
```

---

## 3) Usage Modes

### Mode 1 — Voice Mode
- Speak commands naturally
- Requires microphone
- Best for hands-free usage

### Mode 2 — Text Mode
- Type commands in the console
- Best for testing and development

### Mode 3 — GUI Mode
- Visual interface with buttons and text input
- Manual listen and live status updates
- Best for user-friendly interaction

---

## 4) Skills (What Each Skill Can Do)

### ⏰ Time & Date (skills/time_date.py)
- Current time
- Current date
- Day of the week

Example:
- "What time is it?"
- "What is today's date?"

### 📱 Applications (skills/applications.py)
- Open system apps
- Launch browser, notepad, calculator

Example:
- "Open notepad"
- "Launch calculator"

### 💻 System Info (skills/system.py)
- CPU usage
- Memory usage
- System stats

Example:
- "System status"
- "CPU usage"

### 🌐 Web (skills/web.py)
- Web search
- Open common websites

Example:
- "Search Python tutorials"
- "Open YouTube"

### 📁 Files (skills/files.py)
- Create files
- Create folders
- Screenshots

Example:
- "Create file test.txt"
- "Create folder my_project"

### 🌦️ Weather (skills/weather.py)
- Current weather
- Requires API key in config

Example:
- "What's the weather in London?"

### 🧠 Knowledge (skills/knowledge.py)
- General facts
- Definitions
- Explanations

Example:
- "Who is Albert Einstein?"
- "What is machine learning?"

---

## 5) Tasks (What Tasks Can Be Performed)

Tasks are the executable units created from your input. JARVIS supports:

### Single tasks
- Time lookup
- Open app
- Search the web
- File/folder creation
- System status
- Weather lookup
- Knowledge Q&A

### Multi-step tasks
- Sequence of actions in one request

Examples:
- "Open notepad and search Python"
- "Get weather and tell me the time"

### Task Execution Flow
1. Parse input
2. Create task list
3. Execute tasks in order
4. Return combined response

---

## 6) How Skills Are Used (Skill Routing)

JARVIS decides which skill should handle a command based on keywords and intent matching.

Example:
- "What time is it?" → Time & Date Skill
- "Open notepad" → Applications Skill
- "Create folder docs" → Files Skill

If a request has multiple actions, each action is routed to the correct skill and executed in order.

---

## 7) Commands and Examples

### Time/Date
- "What time is it?"
- "Tell me today's date"

### Applications
- "Open notepad"
- "Launch calculator"

### System Info
- "System status"
- "Memory usage"

### Web
- "Search AI tutorials"
- "Open Google"

### Files
- "Create file notes.txt"
- "Create folder my_files"

### Weather
- "What's the weather in Paris?"

### Knowledge
- "Who is Ada Lovelace?"
- "Explain neural networks"

### Multi-step
- "Open notepad and search Python"
- "Create file test.txt then open calculator"

---

## 8) Configuration

Copy the example config and edit your local file:

```
copy jarvis_config.example.json jarvis_config.json
```

Then edit jarvis_config.json to customize behavior:

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

---

## 9) Help & Troubleshooting

### Microphone not working
- Use Text Mode first
- Check system microphone permissions

### Module import errors
- Reinstall dependencies:
  ```
  pip install -r requirements.txt --force-reinstall
  ```

### Skills not responding
- Verify skill registration in executor.py
- Confirm command keywords match the skill

### GUI not launching
- Ensure Tkinter is installed

---

## 10) FAQ

**Q: Can I add my own skill?**
Yes. Create a new skill file, register it in the executor, and add your logic.

**Q: Does it support multi-step tasks?**
Yes. Combine actions using words like "and" or "then".

**Q: Is an internet connection required?**
Only for web search, knowledge, and weather.

---

## 11) Advanced Tips

- Use short commands in Text Mode for faster testing
- Combine actions to save time
- Use GUI for a clean, visual experience

---

## ✅ Help Summary (Quick Reference)

- Start: python executor.py
- Text mode: Select 2
- Voice mode: Select 1
- GUI: python jarvis_ui.py
- Configure: jarvis_config.json
- Extend: Add a skill in skills/

---

**Last Updated:** February 5, 2026
