# LYRA - Your Personal AI Assistant

LYRA is a desktop-based personal AI assistant built with Python. She can perform basic tasks, open applications, search the web, and more, all controlled by your voice.

## Features
- **Voice Activated:** Listens for the wake word "Lyra".
- **Basic Skills:** Can tell the time and date.
- **Desktop Automation:** Opens installed applications and can type for you.
- **Web Search:** Can search Wikipedia and Google for information.
- **Cost-Free:** Built entirely with free and open-source libraries.

## Setup
1.  **Clone the repository** or download the files.
2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3.  **Install the required libraries**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the assistant**:
    ```bash
    python main.py
    ```

## How to Use
1.  Run `main.py`.
2.  Say a wake word, like "**Hey Lyra**".
3.  LYRA will respond with "Yes, Chief?".
4.  Give your command, for example:
    - "What's the time?"
    - "Open Notepad"
    - "Search Wikipedia for Albert Einstein"