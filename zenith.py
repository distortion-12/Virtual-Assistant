#!/usr/bin/env python3
"""
ZENITH - A Personal Intelligent System
A voice-controlled personal assistant that can fully control your device
"""

import os
import sys
import subprocess
import webbrowser
import datetime
import platform
import json
import glob
from pathlib import Path
from urllib.parse import quote
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

# Optional imports with fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed. System info features will be limited.")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not installed. Text-to-speech will be disabled.")

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("Warning: SpeechRecognition not installed. Voice mode will be disabled.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not installed. Weather features will be disabled.")


class Zenith:
    """Main Zenith Assistant Class"""
    
    def __init__(self):
        """Initialize Zenith with necessary components"""
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
            except Exception as e:
                print(f"Warning: Could not initialize text-to-speech: {e}")
                self.engine = None
        else:
            self.engine = None
        
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
            
        self.config = self.load_config()
        
        if self.engine:
            self.setup_voice()

        self.last_request = ""
        self.last_task_command = ""
        self.last_message = ""
        self.last_contact = ""
        
        # Detect installed applications
        self.installed_apps = self.detect_installed_apps()
        if self.installed_apps:
            print(f"Detected {len(self.installed_apps)} installed applications")
        
    def load_config(self):
        """Load configuration from config file"""
        config_path = Path(__file__).parent / "zenith_config.json"
        fallback_path = Path(__file__).parent / "jarvis_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        if fallback_path.exists():
            with open(fallback_path, 'r') as f:
                return json.load(f)
        return {
            "wake_word": "zenith",
            "voice_rate": 150,
            "voice_volume": 0.9,
            "weather_api_key": ""
        }
    
    def setup_voice(self):
        """Configure text-to-speech settings"""
        if not self.engine:
            return
            
        voices = self.engine.getProperty('voices')
        # Try to set male voice if available
        for voice in voices:
            if 'male' in voice.name.lower() and 'female' not in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', self.config.get('voice_rate', 150))
        self.engine.setProperty('volume', self.config.get('voice_volume', 0.9))
    
    def speak(self, text):
        """Convert text to speech"""
        speak_text = text
        try:
            if not self.config.get("speak_task_details", True):
                question_words = ["who", "what", "why", "how", "when", "where"]
                request = (self.last_request or "").lower()
                small_talk_phrases = [
                    "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                    "good night", "thanks", "thank you", "ok", "okay", "bye", "goodbye",
                    "nice to meet you", "pleased to meet you", "how are you", "what's up",
                    "whats up", "sup"
                ]
                is_small_talk = any(phrase in request for phrase in small_talk_phrases)
                negative_feedback = any(phrase in request for phrase in [
                    "not sent", "wasn't sent", "was not sent", "didn't send", "failed", "not done"
                ])
                is_question = any(word in request for word in question_words)
                if negative_feedback:
                    speak_text = "Okay"
                elif not is_question and not is_small_talk:
                    task_name = self.last_task_command or "Task"
                    if task_name.lower().startswith("send"):
                        speak_text = "Message send attempted"
                    else:
                        speak_text = f"Done {task_name}"
        except Exception:
            speak_text = text

        print(f"Zenith: {speak_text}")
        if self.engine:
            try:
                self.engine.say(speak_text)
                self.engine.runAndWait()
            except Exception as e:
                # If TTS fails, text output is already printed
                pass
    
    def listen(self):
        """Listen for voice commands"""
        if not SR_AVAILABLE or not self.recognizer:
            self.speak("Voice recognition not available. Please use text mode.")
            return ""
            
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                return command
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.speak("Sorry, speech service is unavailable")
                return ""
    
    def get_text_input(self):
        """Get text input from user"""
        return input("Enter command: ").lower()
    
    # ============= DEVICE CONTROL FEATURES =============
    
    def detect_installed_apps(self):
        """Detect ALL installed applications on Windows"""
        installed_apps = {}
        
        if platform.system() != 'Windows':
            return installed_apps
        
        if not WINREG_AVAILABLE:
            return installed_apps
        
        # Check Windows Registry for installed applications
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hkey, reg_path in registry_paths:
            try:
                reg_key = winreg.OpenKey(hkey, reg_path)
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(reg_key, i)
                        sub_key = winreg.OpenKey(reg_key, sub_key_name)
                        try:
                            app_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            
                            # Skip only obvious system components
                            skip_keywords = ['update for', 'kb', 'hotfix', 'security update',
                                           'language pack', 'microsoft visual c++ 20',
                                           'python 3.1', 'python 3.13', 'python 3.12',
                                           'microsoft .net', 'office 16 click-to-run']
                            if any(keyword in app_name.lower() for keyword in skip_keywords):
                                sub_key.Close()
                                continue
                            
                            install_location = None
                            try:
                                install_location = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                            except:
                                pass
                            
                            # Create a simple key from the app name
                            simple_key = app_name.lower().replace(' ', '').replace('.', '')
                            
                            # Only add if not already present (avoid duplicates)
                            if simple_key not in installed_apps:
                                installed_apps[simple_key] = {
                                    'name': app_name,
                                    'display_name': app_name,
                                    'location': install_location,
                                    'simple_name': app_name.split()[0].lower() if app_name.split() else app_name.lower(),
                                    'type': 'desktop'
                                }
                        except:
                            pass
                        sub_key.Close()
                    except:
                        pass
                reg_key.Close()
            except Exception as e:
                pass
        
        # Also check for ALL Microsoft Store apps
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-AppxPackage | Select-Object Name, PackageFullName | ConvertTo-Json'],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                import json as json_module
                store_apps = json_module.loads(result.stdout)
                if isinstance(store_apps, dict):
                    store_apps = [store_apps]
                
                # Skip system/Windows apps
                skip_store_keywords = ['microsoft.windows', 'microsoft.ui', 'microsoft.vclibs',
                                      'microsoft.net', 'windows.', 'microsoft.desktopappinstaller',
                                      'microsoft.windbg', 'microsoft.paint', 'microsoft.screenshot',
                                      'microsoft.people', 'deleteduseraccounts', 'assignedaccess',
                                      'microsoft.accountscontrol', 'microsoft.bioenrollment',
                                      'microsoft.cloudexperience', 'microsoft.credentialdialog',
                                      'microsoft.services.store', 'microsoft.win32webviewhost',
                                      'microsoft.asynctextservice', 'microsoft.ecapp',
                                      'microsoft.lockapp', 'microsoft.aad', 'microsoft.windows.search',
                                      '.singleton', 'e2a4f912', 'f46d4000', 'c5e2524a', '1527c705',
                                      'stable-', '-', 'applicationcompatibility', 'brokerPlugin',
                                      'inputapp', 'contentdeliverymanager', 'parentalcontrols',
                                      'ppiProjection', 'secHealthUi', 'capturePicke', 'xaml']
                
                for app in store_apps:
                    app_name = app.get('Name', '')
                    package_name = app.get('PackageFullName', '')
                    
                    # Skip system apps
                    if any(keyword in app_name.lower() for keyword in skip_store_keywords):
                        continue
                    
                    # Try to extract a friendly name
                    friendly_name = app_name
                    
                    # Common app name mappings
                    name_lower = app_name.lower()
                    if 'whatsapp' in name_lower:
                        friendly_name = 'WhatsApp'
                    elif 'telegram' in name_lower:
                        friendly_name = 'Telegram'
                    elif 'spotify' in name_lower:
                        friendly_name = 'Spotify'
                    elif 'netflix' in name_lower:
                        friendly_name = 'Netflix'
                    elif 'zoom' in name_lower:
                        friendly_name = 'Zoom'
                    elif 'teams' in name_lower:
                        friendly_name = 'Microsoft Teams'
                    elif 'xbox' in name_lower:
                        friendly_name = 'Xbox'
                    elif 'camera' in name_lower:
                        friendly_name = 'Camera'
                    elif 'photos' in name_lower:
                        friendly_name = 'Photos'
                    elif 'calculator' in name_lower and 'windowscalculator' in name_lower:
                        friendly_name = 'Calculator (Store)'
                    elif 'notepad' in name_lower and 'windownotepad' in name_lower:
                        friendly_name = 'Notepad (Store)'
                    elif 'terminal' in name_lower and 'windowsterminal' in name_lower:
                        friendly_name = 'Windows Terminal'
                    elif 'store' in name_lower and 'windowsstore' in name_lower:
                        friendly_name = 'Microsoft Store'
                    elif '.' in app_name:
                        # Extract from package name (e.g., "CompanyName.AppName" -> "AppName")
                        parts = app_name.split('.')
                        if len(parts) >= 2:
                            friendly_name = parts[-1]
                    
                    simple_key = friendly_name.lower().replace(' ', '').replace('.', '').replace('(', '').replace(')', '')
                    
                    # Skip apps with weird/system names or too short names
                    if (len(simple_key) < 3 or 
                        simple_key.isdigit() or
                        any(c in simple_key for c in ['-', '_']) and len(simple_key) < 10):
                        continue
                    
                    # Avoid duplicates
                    if simple_key not in installed_apps and len(friendly_name) > 2:
                        installed_apps[simple_key] = {
                            'name': friendly_name,
                            'display_name': friendly_name,
                            'location': None,
                            'simple_name': friendly_name.split()[0].lower() if friendly_name.split() else friendly_name.lower(),
                            'type': 'store',
                            'package_name': package_name
                        }
        except Exception as e:
            # Store app detection failed, continue without them
            pass
        
        return installed_apps
    
    def open_application(self, app_name):
        """Open applications on the device"""
        aliases = {
            'vs code': 'visual studio code',
            'vscode': 'visual studio code',
            'visual studio': 'visual studio code',
            'ms edge': 'microsoft edge',
            'edge': 'microsoft edge',
            'chrome': 'google chrome',
        }
        app_name = aliases.get(app_name.lower().strip(), app_name)
        # Built-in Windows apps that don't require installation detection
        builtin_apps = {
            'notepad': 'notepad.exe' if platform.system() == 'Windows' else 'gedit',
            'calculator': 'calc.exe' if platform.system() == 'Windows' else 'gnome-calculator',
            'browser': 'chrome' if platform.system() == 'Windows' else 'google-chrome',
            'terminal': 'cmd.exe' if platform.system() == 'Windows' else 'gnome-terminal',
            'file explorer': 'explorer.exe' if platform.system() == 'Windows' else 'nautilus',
        }
        
        # Check if it's a built-in app
        app = builtin_apps.get(app_name.lower())
        if app:
            try:
                if platform.system() == 'Windows':
                    subprocess.Popen(app)
                else:
                    subprocess.Popen([app])
                response = f"Opening {app_name}"
                self.speak(response)
                return response
            except Exception as e:
                response = f"Could not open {app_name}: {str(e)}"
                self.speak(response)
                return response
        
        # Check if it's a detected installed app
        app_key = app_name.lower().replace(' ', '').replace('.', '')
        
        # Try exact match first
        if app_key in self.installed_apps:
            app_info = self.installed_apps[app_key]
        else:
            # Try fuzzy matching - check if app_name is in any detected app's name
            app_info = None
            for key, info in self.installed_apps.items():
                if (app_name.lower() in info['display_name'].lower() or 
                    app_name.lower() == info['simple_name'] or
                    info['simple_name'].startswith(app_name.lower())):
                    app_info = info
                    break
        
        if app_info:
            # Get the app type (desktop or store)
            app_type = app_info.get('type', 'desktop')
            install_location = app_info.get('location')
            
            try:
                # Handle Store apps differently
                if app_type == 'store':
                    package_name = app_info.get('package_name', '')
                    display_name = app_info['display_name']
                    
                    try:
                        # Method 0: Start Menu AppID (best for Store apps)
                        app_id = self._get_start_menu_app_id(display_name)
                        if app_id:
                            subprocess.Popen(
                                f'explorer.exe "shell:AppsFolder\\{app_id}"',
                                shell=True
                            )
                            response = f"Opening {display_name}"
                            self.speak(response)
                            return response

                        # Method 1: Use os.startfile with shell protocol
                        # Extract package family name (remove version number)
                        # Format: Name_Version_Architecture__PublisherId
                        # We need: Name_PublisherId!App
                        parts = package_name.split('_')
                        if len(parts) >= 2:
                            # Get first part (name) and last part (publisher id)
                            package_family = f"{parts[0]}_{parts[-1]}"
                            app_uri = f"shell:AppsFolder\\{package_family}"
                            
                            # Use os.startfile which is better for Windows
                            os.startfile(app_uri)
                            response = f"Opening {display_name}"
                            self.speak(response)
                            return response
                    except Exception as e1:
                        try:
                            # Method 2: Try common execution aliases
                            aliases = {
                                'whatsapp': 'whatsapp:',
                                'telegram': 'tg:',
                                'spotify': 'spotify:',
                                'xbox': 'xbox:',
                            }
                            simple_name = app_info['simple_name']
                            if simple_name in aliases:
                                os.startfile(aliases[simple_name])
                                response = f"Opening {display_name}"
                                self.speak(response)
                                return response
                        except Exception as e2:
                            pass
                        
                        # Method 3: Last resort - use start command
                        subprocess.Popen(f'start {simple_name}', shell=True)
                        response = f"Attempting to open {display_name}"
                        self.speak(response)
                        return response
                
                # Handle desktop apps
                # Try to find the executable
                if install_location and os.path.exists(install_location):
                    # Look for .exe files in the install location
                    exe_files = glob.glob(os.path.join(install_location, "*.exe"))
                    if exe_files:
                        subprocess.Popen(exe_files[0])
                        response = f"Opening {app_info['display_name']}"
                        self.speak(response)
                        return response
                
                # Fallback: try to use shell command
                subprocess.Popen(f'start {app_name}', shell=True)
                response = f"Opening {app_info['display_name']}"
                self.speak(response)
                return response
            except Exception as e:
                response = f"Could not open {app_name}: {str(e)}"
                self.speak(response)
                return response
        else:
            # App not found in installed apps
            response = f"I don't know how to open {app_name}. Try saying the exact app name."
            self.speak(response)
            return response

    def _get_start_menu_app_id(self, app_name: str):
        """Get Start Menu AppID for a Windows Store app"""
        if platform.system() != 'Windows':
            return None
        try:
            cmd = (
                'Get-StartApps | '
                f'Where-Object {{$_.Name -match "{app_name}"}} | '
                'Select-Object -First 1 -ExpandProperty AppID'
            )
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                app_id = result.stdout.strip()
                return app_id if app_id else None
        except Exception:
            pass
        return None
    
    def shutdown_system(self, confirmed=False):
        """Shutdown the computer - requires confirmation"""
        if not confirmed:
            self.speak("This action requires explicit confirmation. Not executing for safety.")
            return False
            
        self.speak("Shutting down the system")
        if platform.system() == 'Windows':
            os.system('shutdown /s /t 1')
        else:
            os.system('shutdown now')
        return True
    
    def restart_system(self, confirmed=False):
        """Restart the computer - requires confirmation"""
        if not confirmed:
            self.speak("This action requires explicit confirmation. Not executing for safety.")
            return False
            
        self.speak("Restarting the system")
        if platform.system() == 'Windows':
            os.system('shutdown /r /t 1')
        else:
            os.system('reboot')
        return True
    
    def sleep_system(self, confirmed=False):
        """Put the computer to sleep - requires confirmation"""
        if not confirmed:
            self.speak("This action requires explicit confirmation. Not executing for safety.")
            return False
            
        self.speak("Putting the system to sleep")
        if platform.system() == 'Windows':
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        else:
            os.system('systemctl suspend')
        return True
    
    def adjust_volume(self, action):
        """Adjust system volume"""
        if platform.system() == 'Windows':
            # Note: Requires nircmd.exe on Windows
            # Download from: https://www.nirsoft.net/utils/nircmd.html
            try:
                if action == 'up':
                    subprocess.run(['nircmd.exe', 'changesysvolume', '2000'], check=True)
                elif action == 'down':
                    subprocess.run(['nircmd.exe', 'changesysvolume', '-2000'], check=True)
                elif action == 'mute':
                    subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], check=True)
                self.speak(f"Volume {action}")
            except FileNotFoundError:
                self.speak("Volume control requires nircmd.exe. Please download from nirsoft.net")
            except Exception as e:
                self.speak("Could not adjust volume")
        elif platform.system() == 'Linux':
            try:
                if action == 'up':
                    subprocess.run(['amixer', 'set', 'Master', '5%+'], check=True)
                elif action == 'down':
                    subprocess.run(['amixer', 'set', 'Master', '5%-'], check=True)
                elif action == 'mute':
                    subprocess.run(['amixer', 'set', 'Master', 'toggle'], check=True)
                self.speak(f"Volume {action}")
            except FileNotFoundError:
                self.speak("Volume control requires amixer (alsa-utils package)")
            except Exception as e:
                self.speak("Could not adjust volume")
        elif platform.system() == 'Darwin':  # macOS
            try:
                if action == 'up':
                    subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) + 10)'], check=True)
                elif action == 'down':
                    subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) - 10)'], check=True)
                elif action == 'mute':
                    subprocess.run(['osascript', '-e', 'set volume output muted not (output muted of (get volume settings))'], check=True)
                self.speak(f"Volume {action}")
            except Exception as e:
                self.speak("Could not adjust volume")
        else:
            self.speak("Volume control not implemented for this operating system")
    
    def get_system_info(self):
        """Get system information"""
        if not PSUTIL_AVAILABLE:
            self.speak("System monitoring not available. Please install psutil.")
            return
            
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = f"CPU usage is {cpu_percent} percent. "
        info += f"Memory usage is {memory.percent} percent. "
        info += f"Disk usage is {disk.percent} percent."
        
        self.speak(info)
        return info
    
    def list_running_processes(self):
        """List top running processes"""
        if not PSUTIL_AVAILABLE:
            self.speak("Process monitoring not available. Please install psutil.")
            return
            
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        top_5 = processes[:5]
        
        self.speak("Top 5 processes by CPU usage:")
        for proc in top_5:
            print(f"- {proc['name']}: {proc['cpu_percent']}%")
    
    # ============= TASK EXECUTION FEATURES =============
    
    def get_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        self.speak(f"The current time is {time_str}")
        return time_str
    
    def get_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        self.speak(f"Today is {date_str}")
        return date_str
    
    def search_web(self, query):
        """Search the web"""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        self.speak(f"Searching for {query}")
    
    def search_knowledge(self, query):
        """Search for knowledge-based answers (uses Wikipedia)"""
        def _normalize_query(q: str) -> str:
            q = q.strip().lower()
            prefixes = [
                "who is ", "what is ", "why is ", "how is ",
                "who are ", "what are ", "why are ", "how are ",
                "tell me about ", "information about ",
            ]
            for p in prefixes:
                if q.startswith(p):
                    q = q[len(p):]
                    break
            return q.strip(" ?!.,") or q

        query = _normalize_query(query)
        headers = {
            "User-Agent": "Zenith/1.0 (https://example.com; contact: local)"
        }
        if not REQUESTS_AVAILABLE:
            response = (
                f"I couldn't search online right now. "
                f"Try rephrasing your question about {query}, or ask me to search the web."
            )
            self.speak(response)
            return response
        
        try:
            # First, find the best matching Wikipedia title
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'opensearch',
                'format': 'json',
                'search': query,
                'limit': 1,
            }
            search_response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
            search_data = search_response.json()
            title = None
            if isinstance(search_data, list) and len(search_data) >= 2 and search_data[1]:
                title = search_data[1][0]

            # Try to get answer from Wikipedia API
            title_to_fetch = title or query
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': title_to_fetch,
                'prop': 'extracts',
                'explaintext': True,
                'exintro': True,
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            # Extract the page content
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'extract' in page_data and page_data['extract']:
                    extract = page_data['extract']
                    # Get first 2-3 sentences
                    sentences = extract.split('.')[:3]
                    answer = '.'.join(sentences).strip()
                    
                    self.speak(answer)
                    return answer

            # Fallback: Wikipedia REST summary
            if title:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
            else:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
            summary_response = requests.get(summary_url, headers=headers, timeout=5)
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                summary_text = summary_data.get('extract')
                if summary_text:
                    self.speak(summary_text)
                    return summary_text
            
            # If no Wikipedia result, search web
            response = (
                f"I couldn't find a concise answer for {query}. "
                "Try rephrasing, or say 'search' followed by your query to open the web."
            )
            self.speak(response)
            return response
            
        except Exception as e:
            response = (
                f"I couldn't find a concise answer for {query}. "
                "Try rephrasing, or say 'search' followed by your query to open the web."
            )
            self.speak(response)
            return response
    
    def open_website(self, url):
        """Open a specific website"""
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        self.speak(f"Opening {url}")
    
    def get_weather(self, city=""):
        """Get weather information"""
        if not REQUESTS_AVAILABLE:
            self.speak("Weather feature not available. Please install requests library.")
            return
            
        api_key = self.config.get('weather_api_key', '')
        if not api_key:
            self.speak("Weather API key not configured")
            return
        
        if not city:
            city = "London"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                self.speak(f"The temperature in {city} is {temp} degrees celsius with {desc}")
            else:
                self.speak("Could not fetch weather information")
        except Exception as e:
            self.speak("Error fetching weather data")
    
    def create_file(self, filename):
        """Create a new file"""
        try:
            Path(filename).touch()
            self.speak(f"File {filename} created")
        except Exception as e:
            self.speak(f"Could not create file {filename}")
    
    def create_folder(self, foldername):
        """Create a new folder"""
        try:
            Path(foldername).mkdir(exist_ok=True)
            self.speak(f"Folder {foldername} created")
        except Exception as e:
            self.speak(f"Could not create folder {foldername}")
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            import pyautogui
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            self.speak(f"Screenshot saved as {filename}")
        except ImportError:
            self.speak("Screenshot feature requires pyautogui. Please install it.")
        except Exception as e:
            self.speak("Could not take screenshot")
    
    # ============= COMMAND PROCESSING =============
    
    # Legacy method - kept for backward compatibility
    def process_command(self, command):
        """Legacy command processing - use agents instead"""
        self.speak("Please use the new agent-based system. Run: python executor.py")
        return False
