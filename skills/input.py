"""
Input and Typing Skill
Handles typing text into the active window
"""

from typing import Optional
import os

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
from .base_skill import BaseSkill, SkillResult


class InputSkill(BaseSkill):
    """Skill for typing text into the active window"""

    def can_handle(self, command: str) -> bool:
        """Check if command is about typing text"""
        cmd = command.lower()
        keywords = ['write', 'type', 'enter', 'input', 'write down']
        return any(keyword in cmd for keyword in keywords)

    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute typing command"""
        cmd = command.strip()
        cmd_lower = cmd.lower()

        code_topic = self._extract_code_topic(cmd)
        is_code_task = bool(code_topic)
        if code_topic:
            language = self._extract_language(cmd_lower)
            text = self._generate_code_with_ai(code_topic, language)
            if not text:
                response = "AI code generation failed. Check API key/model and try again."
                self.speak(response)
                return response
        else:
            text = self._extract_text(cmd)

        if not text:
            response = "What would you like me to type?"
            self.speak(response)
            return response

        try:
            import pyautogui
            import time
            import tkinter as tk
        except ImportError:
            response = "Typing requires pyautogui. Please install it."
            self.speak(response)
            return response

        try:
            try:
                windows = pyautogui.getWindowsWithTitle("Notepad")
                if windows:
                    windows[0].activate()
                    time.sleep(0.5)
            except Exception:
                pass

            time.sleep(0.8)

            pasted = self._paste_text_in_chunks(text, tk, pyautogui, time)
            if not pasted:
                pyautogui.write(text, interval=0.01)

            if is_code_task:
                response = "Code typed."
            else:
                response = f"Typed: {text}"

            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not type the text: {e}"
            self.speak(response)
            return response

    def _paste_text_in_chunks(self, text: str, tk_module, pyautogui_module, time_module) -> bool:
        """Paste large text reliably by chunking."""
        try:
            chunk_size = 1500
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

            for idx, chunk in enumerate(chunks):
                root = tk_module.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(chunk)
                root.update()
                root.destroy()

                pyautogui_module.hotkey('ctrl', 'v')
                time_module.sleep(0.2)

                if idx < len(chunks) - 1:
                    time_module.sleep(0.2)
            return True
        except Exception:
            return False

    def _extract_text(self, command: str) -> str:
        """Extract text to type from a command"""
        cmd = command.lower()

        prefixes = [
            'write down',
            'write',
            'type',
            'enter',
            'input',
        ]
        text = command
        for prefix in prefixes:
            idx = cmd.find(prefix)
            if idx != -1:
                text = command[idx + len(prefix):]
                break

        text = text.strip()

        fillers = [
            'in notepad',
            'into notepad',
            'in the notepad',
            'into the notepad',
            'in that',
            'over that',
            'there',
            'here',
        ]
        for filler in fillers:
            if text.lower().endswith(filler):
                text = text[: -len(filler)].strip()

        return text

    def _extract_code_topic(self, command: str) -> str:
        """Extract topic for code generation"""
        cmd = command.lower()
        markers = [
            'write code for',
            'type code for',
            'write a code for',
            'write code to',
            'write a code to',
            'generate code for',
            'create code for',
            'code for',
        ]
        for marker in markers:
            if marker in cmd:
                start = cmd.find(marker) + len(marker)
                topic = command[start:].strip()
                return topic.strip(' ?!.')
        return ""

    def _extract_language(self, cmd: str) -> str:
        """Infer language from command"""
        if any(keyword in cmd for keyword in [' html', ' in html', ' html css', ' webpage', ' web page', ' page', ' form', 'signup', 'sign up', 'login']):
            return 'html'
        if ' css' in cmd or ' in css' in cmd:
            return 'html'
        if ' in python' in cmd or ' python' in cmd:
            return 'python'
        if ' in javascript' in cmd or ' javascript' in cmd or ' js' in cmd:
            return 'javascript'
        if ' in java' in cmd or ' java' in cmd:
            return 'java'
        if ' in c++' in cmd or ' c++' in cmd:
            return 'cpp'
        if ' in c#' in cmd or ' c#' in cmd:
            return 'csharp'
        return 'python'

    def _generate_code_with_ai(self, topic: str, language: str) -> str:
        """Generate code using a hosted AI model (Hugging Face Inference API)."""
        if not REQUESTS_AVAILABLE:
            return ""

        config = getattr(self.jarvis, 'config', {}) or {}
        google_api_key = config.get('google_api_key') or os.getenv('GOOGLE_API_KEY')
        google_model = config.get('google_model') or os.getenv('GOOGLE_MODEL') or "gemini-1.5-flash"

        api_token = config.get('hf_api_token') or os.getenv('HF_API_TOKEN')

        primary_model = config.get('hf_code_model') or os.getenv('HF_CODE_MODEL') or "gpt2"
        fallback_models = [
            primary_model,
            "distilgpt2",
        ]
        models_to_try = []
        for m in fallback_models:
            if m and m not in models_to_try:
                models_to_try.append(m)
        max_tokens = int(config.get('hf_code_max_tokens', 400))
        google_max_tokens = int(config.get('google_max_tokens', max_tokens))
        temperature = float(config.get('hf_code_temperature', 0.2))

        prompt = (
            f"Write {language} code for the following task. "
            f"Return only raw code, no markdown, no backticks, no explanations.\n\n"
            f"Task: {topic}\n"
        )

        if language == 'html':
            prompt += (
                "\nReturn a complete single-file HTML document with inline CSS and minimal JS if needed. "
                "Include all required elements for the page to render nicely."
            )

        headers = {
            "User-Agent": "Zenith/1.0 (https://example.com; contact: local)",
        }

        # Try Google Gemini API if configured
        if google_api_key:
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{google_model}:generateContent?key={google_api_key}",
                    headers={
                        **headers,
                        "Content-Type": "application/json",
                    },
                    json={
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": prompt}],
                            }
                        ],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": google_max_tokens,
                        },
                    },
                    timeout=30,
                )
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", []) if isinstance(data, dict) else []
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                            if text:
                                text = self._sanitize_code(text)
                                if language == 'html' and "</html>" not in text.lower():
                                    text = self._continue_with_gemini(
                                        google_api_key,
                                        google_model,
                                        prompt,
                                        text,
                                        temperature,
                                        google_max_tokens,
                                        headers,
                                    )
                                return text
                else:
                    self.log(f"Google code generation failed: HTTP {response.status_code}")
            except Exception as e:
                self.log(f"Google code generation exception: {e}")

        legacy_payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
            },
        }

        if not api_token:
            return ""

        headers["Authorization"] = f"Bearer {api_token}"

        for model in models_to_try:
            for _ in range(3):
                try:
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json=legacy_payload,
                        timeout=30,
                    )

                    if response.status_code == 503:
                        try:
                            data = response.json()
                            wait_time = int(data.get("estimated_time", 3))
                            import time
                            time.sleep(min(wait_time + 1, 8))
                            continue
                        except Exception:
                            import time
                            time.sleep(3)
                            continue

                    if response.status_code != 200:
                        self.log(f"AI code generation failed ({model}): HTTP {response.status_code}")
                        break

                    data = response.json()
                    if isinstance(data, dict) and data.get("error"):
                        self.log(f"AI code generation error ({model}): {data.get('error')}")
                        break

                    generated = ""
                    if isinstance(data, list) and data and isinstance(data[0], dict):
                        generated = data[0].get("generated_text", "")
                    elif isinstance(data, dict):
                        generated = data.get("generated_text", "")

                    if not generated:
                        break

                    return self._sanitize_code(generated)
                except Exception as e:
                    self.log(f"AI code generation exception ({model}): {e}")
                    break

        return ""

    def _continue_with_gemini(
        self,
        api_key: str,
        model: str,
        prompt: str,
        partial: str,
        temperature: float,
        max_tokens: int,
        headers: dict,
    ) -> str:
        """Ask Gemini to continue a truncated code response."""
        try:
            tail = partial[-1500:]
            continuation_prompt = (
                "Continue the code from where it stopped. "
                "Return only the remaining code, no explanations, no markdown.\n\n"
                f"Original task: {prompt}\n\n"
                "Last part of current code:\n"
                f"{tail}\n"
            )
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                headers={
                    **headers,
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": continuation_prompt}],
                        }
                    ],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                },
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", []) if isinstance(data, dict) else []
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        extra = parts[0].get("text", "")
                        if extra:
                            extra = self._sanitize_code(extra)
                            return (partial + "\n" + extra).strip()
        except Exception as e:
            self.log(f"Google continuation exception: {e}")

        return partial

    def _sanitize_code(self, text: str) -> str:
        """Remove markdown fences and trim output."""
        if not text:
            return ""

        cleaned = text.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1].strip()
        cleaned = cleaned.strip("`")
        return cleaned.strip()
