"""
Messaging Skill
Handles sending messages in WhatsApp Desktop
"""

import json
import re
from pathlib import Path
from typing import Optional
from .base_skill import BaseSkill


class MessageSkill(BaseSkill):
    """Skill for sending messages"""

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        return (
            cmd.startswith("send ")
            or ("send" in cmd and " to " in cmd)
            or any(phrase in cmd for phrase in ["not sent", "wasn't sent", "didn't send", "send again", "resend"])
            or "set whatsapp search" in cmd
            or "set whatsapp input" in cmd
            or "set whatsapp chat" in cmd
        )

    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        cmd = self._normalize_command(command)
        if self._is_calibration(cmd):
            return self._handle_calibration(cmd)

        msg, contact = self._parse_message(cmd)

        if self._is_negative_feedback(cmd):
            msg = msg or getattr(self.jarvis, "last_message", "")
            contact = contact or getattr(self.jarvis, "last_contact", "")

        if not msg and not contact:
            response = "Please say: send <message> to <contact>."
            self.speak(response)
            return response

        if self._is_negative_feedback(cmd) and not msg:
            response = "No previous message found. Say: send <message> to <contact>."
            self.speak(response)
            return response

        try:
            import pyautogui
            import time
        except ImportError:
            response = "Messaging requires pyautogui. Please install it."
            self.speak(response)
            return response

        try:
            windows = pyautogui.getWindowsWithTitle("WhatsApp")
            if not windows:
                if not self._open_whatsapp_app():
                    response = "WhatsApp is not open. Please open WhatsApp first."
                    self.speak(response)
                    return response

                time.sleep(1.5)
                windows = pyautogui.getWindowsWithTitle("WhatsApp")
                if not windows:
                    response = "WhatsApp did not open. Please open it manually."
                    self.speak(response)
                    return response

            windows[0].activate()
            time.sleep(1.2)

            if contact:
                if not self._open_chat(pyautogui, time, contact):
                    response = f"Could not open chat for {contact}. Please open it manually."
                    self.speak(response)
                    return response
            else:
                response = "Sending to the currently open chat."
                self.speak(response)

            self._focus_message_box(pyautogui, time)
            pyautogui.write(msg, interval=0.02)
            pyautogui.press('enter')

            try:
                self.jarvis.last_message = msg
                self.jarvis.last_contact = contact
            except Exception:
                pass

            if contact:
                response = f"Attempted to send message to {contact}. Please confirm."
            else:
                response = "Attempted to send message in current chat. Please confirm."
            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not send message: {e}"
            self.speak(response)
            return response

    def _parse_message(self, command: str) -> tuple:
        cmd = command.lower()
        match = re.search(
            r"send\s+(?:a\s+)?(?:whatsapp\s+)?message\s+to\s+(.+?)(?:\s+(?:saying|message)\s+(.+))?$",
            cmd,
        )
        if match:
            contact = match.group(1).strip()
            msg = (match.group(2) or "").strip()
            contact = contact.replace("on whatsapp", "").strip()
            return msg, contact

        match = re.search(r"send\s+(.*?)\s+to\s+(.+)", cmd)
        if not match:
            match_simple = re.search(r"send\s+(.+)", cmd)
            if not match_simple:
                return "", ""
            msg = match_simple.group(1).strip()
            msg = msg.replace("on whatsapp", "").strip()
            return msg, ""
        msg = match.group(1).strip()
        contact = match.group(2).strip()
        contact = contact.replace("on whatsapp", "").strip()
        return msg, contact

    def _normalize_command(self, command: str) -> str:
        cmd = command.strip()
        cmd_lower = cmd.lower()
        if "open whatsapp" in cmd_lower and "send" in cmd_lower:
            parts = re.split(r"open\s+whatsapp\s+and\s+", cmd, flags=re.IGNORECASE)
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip()
        return cmd

    def _open_whatsapp_app(self) -> bool:
        try:
            if hasattr(self.jarvis, "open_application"):
                self.jarvis.open_application("whatsapp")
                return True
        except Exception:
            return False
        return False

    def _should_use_web(self, command: str) -> bool:
        cmd = command.lower()
        config = self._load_config()
        mode = str(config.get("whatsapp_send_mode", "desktop")).lower()
        if mode in ["web", "pywhatkit", "browser"]:
            return True
        return "whatsapp web" in cmd or "whatsapp browser" in cmd or "use web" in cmd

    def _prompt_for_value(self, question: str) -> str:
        self.speak(question)
        response = ""
        try:
            if hasattr(self.jarvis, "listen"):
                response = self.jarvis.listen() or ""
        except Exception:
            response = ""

        if not response:
            try:
                if hasattr(self.jarvis, "get_text_input"):
                    response = self.jarvis.get_text_input() or ""
            except Exception:
                response = ""
        return response.strip()

    def _load_contacts(self) -> dict:
        config = self._load_config()
        contacts = config.get("whatsapp_contacts", {})
        return contacts if isinstance(contacts, dict) else {}

    def _normalize_phone(self, phone: str) -> str:
        phone_clean = re.sub(r"[^0-9+]", "", phone)
        if phone_clean.startswith("+"):
            return phone_clean

        config = self._load_config()
        default_code = str(config.get("default_country_code", "")).strip()
        if default_code and not default_code.startswith("+"):
            default_code = f"+{default_code}"
        if default_code:
            return f"{default_code}{phone_clean}"
        return f"+{phone_clean}"

    def _resolve_contact(self, contact: str) -> str:
        contact = contact.strip()
        if not contact:
            return ""

        contacts = self._load_contacts()
        if contact in contacts:
            return self._normalize_phone(str(contacts[contact]))

        if re.match(r"^\+?\d[\d\s\-]{6,}$", contact):
            return self._normalize_phone(contact)

        return ""

    def _send_whatsapp_web(self, msg: str, contact: str) -> Optional[str]:
        if not contact:
            contact = self._prompt_for_value("Whom do you want to send a WhatsApp message to?")

        if not msg:
            msg = self._prompt_for_value("What is the message?")

        if not msg or not contact:
            response = "Please provide both a contact and a message."
            self.speak(response)
            return response

        phone_no = self._resolve_contact(contact)
        if not phone_no:
            response = "Contact not found. Add it to whatsapp_contacts in jarvis_config.json or say a phone number."
            self.speak(response)
            return response

        try:
            import pywhatkit
        except ImportError:
            response = "WhatsApp Web messaging requires pywhatkit. Please install it."
            self.speak(response)
            return response

        config = self._load_config()
        wait_time = int(config.get("whatsapp_web_wait_time", 15))
        close_tab = bool(config.get("whatsapp_web_close_tab", True))
        close_time = int(config.get("whatsapp_web_close_time", 3))

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no,
                msg,
                wait_time=wait_time,
                tab_close=close_tab,
                close_time=close_time,
            )

            try:
                self.jarvis.last_message = msg
                self.jarvis.last_contact = contact
            except Exception:
                pass

            response = f"Attempted to send WhatsApp message to {contact}. Please confirm."
            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not send WhatsApp message: {e}"
            self.speak(response)
            return response

    def _focus_message_box(self, pyautogui_module, time_module):
        """Try to focus the WhatsApp message input box."""
        try:
            config = self._load_config()
            pos = config.get("whatsapp_input_pos")
            if isinstance(pos, list) and len(pos) == 2:
                pyautogui_module.click(pos[0], pos[1])
                time_module.sleep(0.5)
                return

            active = pyautogui_module.getActiveWindow()
            if active:
                x = active.left + active.width // 2
                y = active.top + active.height - 80
                pyautogui_module.click(x, y)
                time_module.sleep(0.2)
        except Exception:
            pass

    def _open_chat(self, pyautogui_module, time_module, contact: str) -> bool:
        """Open a WhatsApp chat using the search bar."""
        try:
            config = self._load_config()
            debug = bool(config.get("whatsapp_debug", False))
            pos = config.get("whatsapp_search_pos")
            chat_pos = config.get("whatsapp_chat_pos")
            has_search_pos = isinstance(pos, list) and len(pos) == 2
            has_chat_pos = isinstance(chat_pos, list) and len(chat_pos) == 2

            if has_search_pos:
                pyautogui_module.click(pos[0], pos[1])
                time_module.sleep(0.2)
                if debug:
                    self.log(f"Using configured search pos: {pos}")

            if has_search_pos:
                pyautogui_module.hotkey('ctrl', 'f')
                time_module.sleep(0.6)
            else:
                pyautogui_module.hotkey('ctrl', 'n')
                time_module.sleep(0.8)

            pyautogui_module.hotkey('ctrl', 'a')
            pyautogui_module.press('backspace')
            time_module.sleep(0.5)
            pyautogui_module.write(contact, interval=0.02)
            time_module.sleep(1.8)

            if has_chat_pos:
                pyautogui_module.doubleClick(chat_pos[0], chat_pos[1])
                time_module.sleep(1.5)
                if debug:
                    self.log(f"Using configured chat pos: {chat_pos}")
            else:
                pyautogui_module.press('enter')
                time_module.sleep(1.2)

            time_module.sleep(1.2)
            if has_search_pos:
                pyautogui_module.press('esc')
                time_module.sleep(0.5)
            if debug:
                active = pyautogui_module.getActiveWindow()
                title = active.title if active else ""
                self.log(f"Active window after search: {title}")
            return True
        except Exception:
            return False

    def _is_calibration(self, command: str) -> bool:
        cmd = command.lower()
        return "set whatsapp search" in cmd or "set whatsapp input" in cmd or "set whatsapp chat" in cmd

    def _handle_calibration(self, command: str) -> str:
        try:
            import pyautogui
            import time
        except ImportError:
            response = "Calibration requires pyautogui. Please install it."
            self.speak(response)
            return response

        cmd = command.lower()
        if "set whatsapp search" in cmd:
            self.speak("Hover your mouse over the WhatsApp search box. Capturing in 3 seconds.")
            time.sleep(3)
            pos = list(pyautogui.position())
            self._update_config({"whatsapp_search_pos": pos})
            response = "WhatsApp search position saved."
            self.speak(response)
            return response

        if "set whatsapp input" in cmd:
            self.speak("Hover your mouse over the WhatsApp message input box. Capturing in 3 seconds.")
            time.sleep(3)
            pos = list(pyautogui.position())
            self._update_config({"whatsapp_input_pos": pos})
            response = "WhatsApp input position saved."
            self.speak(response)
            return response

        if "set whatsapp chat" in cmd:
            self.speak("Hover your mouse over the first chat result in the list. Capturing in 3 seconds.")
            time.sleep(3)
            pos = list(pyautogui.position())
            self._update_config({"whatsapp_chat_pos": pos})
            response = "WhatsApp chat position saved."
            self.speak(response)
            return response

        response = "Calibration command not recognized."
        self.speak(response)
        return response

    def _load_config(self) -> dict:
        try:
            config_path = Path(__file__).parent.parent / "jarvis_config.json"
            if config_path.exists():
                return json.loads(config_path.read_text())
        except Exception:
            pass
        return {}

    def _update_config(self, updates: dict) -> None:
        try:
            config_path = Path(__file__).parent.parent / "jarvis_config.json"
            data = {}
            if config_path.exists():
                data = json.loads(config_path.read_text())
            data.update(updates)
            config_path.write_text(json.dumps(data, indent=4))
        except Exception:
            pass

    def _is_negative_feedback(self, command: str) -> bool:
        cmd = command.lower()
        return any(phrase in cmd for phrase in ["not sent", "wasn't sent", "didn't send", "resend", "send again"])
