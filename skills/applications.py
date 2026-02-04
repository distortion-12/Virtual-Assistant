"""
Application Control Skill
Handles opening and managing applications
"""

import subprocess
import platform
import os
import winreg
from typing import Optional
from pathlib import Path
from .base_skill import BaseSkill, SkillResult


class ApplicationSkill(BaseSkill):
    """Skill for handling application control"""
    
    APPLICATIONS = {
        'notepad': {
            'windows': 'notepad.exe',
            'linux': 'gedit',
            'darwin': 'TextEdit',
        },
        'calculator': {
            'windows': 'calc.exe',
            'linux': 'gnome-calculator',
            'darwin': 'Calculator',
        },
        'browser': {
            'windows': 'chrome',
            'linux': 'google-chrome',
            'darwin': 'safari',
        },
        'chrome': {
            'windows': 'chrome',
            'linux': 'google-chrome',
            'darwin': 'Google Chrome',
        },
        'firefox': {
            'windows': 'firefox.exe',
            'linux': 'firefox',
            'darwin': 'Firefox',
        },
        'edge': {
            'windows': 'msedge.exe',
            'linux': 'microsoft-edge',
            'darwin': 'Microsoft Edge',
        },
        'terminal': {
            'windows': 'cmd.exe',
            'linux': 'gnome-terminal',
            'darwin': 'Terminal',
        },
        'file explorer': {
            'windows': 'explorer.exe',
            'linux': 'nautilus',
            'darwin': 'Finder',
        },
        'files': {
            'windows': 'explorer.exe',
            'linux': 'nautilus',
            'darwin': 'Finder',
        },
        'vscode': {
            'windows': 'code.exe',
            'linux': 'code',
            'darwin': 'Visual Studio Code',
        },
        'vs code': {
            'windows': 'code.exe',
            'linux': 'code',
            'darwin': 'Visual Studio Code',
        },
        'visual studio code': {
            'windows': 'code.exe',
            'linux': 'code',
            'darwin': 'Visual Studio Code',
        },
        'whatsapp': {
            'windows': 'whatsapp',  # Will use Windows app search
            'linux': 'WhatsApp',
            'darwin': 'WhatsApp',
        },
        'spotify': {
            'windows': 'spotify.exe',
            'linux': 'spotify',
            'darwin': 'Spotify',
        },
        'discord': {
            'windows': 'discord.exe',
            'linux': 'Discord',
            'darwin': 'Discord',
        },
        'slack': {
            'windows': 'slack.exe',
            'linux': 'slack',
            'darwin': 'Slack',
        },
        'teams': {
            'windows': 'teams.exe',
            'linux': 'teams',
            'darwin': 'Microsoft Teams',
        },
        'zoom': {
            'windows': 'zoom.exe',
            'linux': 'zoom',
            'darwin': 'zoom.us',
        },
    }
    
    def can_handle(self, command: str) -> bool:
        """Check if command is to open or close an application"""
        cmd = command.lower()
        return any(keyword in cmd for keyword in ['open', 'launch', 'start', 'close', 'quit', 'exit'])
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute application control command"""
        cmd = command.lower()

        # Remove common natural language modifiers
        modifiers = ['please', 'can you', 'could you', 'will you', 'would you', 'kindly', 'thanks']
        for modifier in modifiers:
            cmd = cmd.replace(modifier, '')

        if any(keyword in cmd for keyword in ['close', 'quit', 'exit']):
            app_name = self._extract_app_name(cmd, ['close', 'quit', 'exit'])
            return self.close_application(app_name)

        # Default: open/launch/start
        app_name = self._extract_app_name(cmd, ['open', 'launch', 'start'])
        return self.open_application(app_name)

    def _extract_app_name(self, cmd: str, verbs: list) -> str:
        """Extract app name from a command"""
        app_name = cmd
        for verb in verbs:
            app_name = app_name.replace(verb, '')
        app_name = app_name.strip()

        articles = ['the', 'a', 'an']
        for article in articles:
            if app_name.startswith(article + ' '):
                app_name = app_name[len(article) + 1:].strip()

        return app_name
    
    def _find_app_in_registry(self, app_name: str) -> Optional[str]:
        """Search Windows registry for application path"""
        if platform.system().lower() != 'windows':
            return None
        
        try:
            # Search in HKEY_LOCAL_MACHINE
            registry_paths = [
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths',
            ]
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    subkeys = winreg.QueryValueEx(key, app_name)
                    if subkeys:
                        return subkeys[0]
                except:
                    continue
        except:
            pass
        
        return None
    
    def _find_app_in_path(self, app_name: str) -> Optional[str]:
        """Search PATH environment variable for executable"""
        result = subprocess.run(['where', app_name], 
                              capture_output=True, 
                              text=True,
                              shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
        return None

    def _find_start_menu_app_id(self, app_name: str) -> Optional[str]:
        """Find Windows Start Menu AppID for Store apps"""
        if platform.system().lower() != 'windows':
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
    
    def _launch_windows_app(self, app_path: str, app_name: str) -> str:
        """Launch application on Windows with multiple strategies"""
        system = platform.system().lower()
        
        if system != 'windows':
            try:
                subprocess.Popen([app_path])
                response = f"Opening {app_name}"
                self.speak(response)
                return response
            except Exception as e:
                response = f"Could not open {app_name}: {e}"
                self.speak(response)
                return response
        
        # Windows-specific strategies
        strategies = [
            # Strategy 1: Direct execution if it's in PATH
            lambda: subprocess.Popen(app_path, shell=True) if self._find_app_in_path(app_path) else None,
            
            # Strategy 2: Registry lookup for app paths
            lambda: subprocess.Popen(self._find_app_in_registry(app_path.split('.')[0])) if self._find_app_in_registry(app_path.split('.')[0]) else None,
            
            # Strategy 3: Try common installation paths
            lambda: self._try_common_paths(app_name, app_path),

            # Strategy 4: Start Menu AppID (Store apps)
            lambda: subprocess.Popen(
                f'explorer.exe "shell:AppsFolder\\{self._find_start_menu_app_id(app_name)}"',
                shell=True
            ) if self._find_start_menu_app_id(app_name) else None,
            
            # Strategy 5: Use 'start' command for modern apps and shortcuts
            lambda: subprocess.Popen(f'start "" "{app_path}"', shell=True),
        ]
        
        last_error = None
        for strategy in strategies:
            try:
                result = strategy()
                # Only report success if something actually returned (not None)
                if result is not None:
                    response = f"Opening {app_name}"
                    self.speak(response)
                    return response
            except Exception as e:
                last_error = e
                continue
        
        # App not found - provide helpful message
        response = f"{app_name.capitalize()} is not installed on this system. "
        response += f"Please install {app_name} and try again."
        self.speak(response)
        return response
    
    def _try_common_paths(self, app_name: str, app_path: str) -> Optional[subprocess.Popen]:
        """Try common installation paths for Windows apps"""
        app_lower = app_name.lower()
        
        common_paths = {
            'whatsapp': [
                str(Path.home() / 'AppData/Local/WhatsApp/WhatsApp.exe'),
                str(Path.home() / 'AppData/Local/Microsoft/WindowsApps/WhatsApp.exe'),
            ],
            'spotify': [
                str(Path.home() / 'AppData/Roaming/Spotify/spotify.exe'),
                str(Path.home() / 'AppData/Local/Spotify/Spotify.exe'),
            ],
            'discord': [
                str(Path.home() / 'AppData/Local/Discord/app-1.0.x/Discord.exe'),
                str(Path.home() / 'AppData/Local/Discord/Update.exe'),
            ],
            'slack': [
                str(Path.home() / 'AppData/Local/slack/slack.exe'),
            ],
        }
        
        if app_lower in common_paths:
            for path in common_paths[app_lower]:
                try:
                    # Check if path exists before trying to open
                    if Path(path).exists():
                        return subprocess.Popen(path, shell=True)
                except:
                    continue
        
        return None
    
    def open_application(self, app_name: str) -> str:
        """Open a specific application"""
        app_name = app_name.lower().strip()
        aliases = {
            'vs code': 'visual studio code',
            'vscode': 'visual studio code',
            'visual studio': 'visual studio code',
            'ms edge': 'microsoft edge',
            'edge': 'microsoft edge',
            'chrome': 'google chrome',
        }
        app_name = aliases.get(app_name, app_name)
        
        if app_name not in self.APPLICATIONS:
            response = f"I don't know how to open {app_name}"
            self.speak(response)
            return response
        
        system = platform.system().lower()
        if system == 'darwin':
            system = 'darwin'
        else:
            system = 'windows' if system == 'windows' else 'linux'
        
        app_path = self.APPLICATIONS[app_name].get(system)
        
        if not app_path:
            response = f"Application not available for your system"
            self.speak(response)
            return response
        
        return self._launch_windows_app(app_path, app_name)

    def close_application(self, app_name: str) -> str:
        """Close a specific application"""
        app_name = app_name.lower().strip()

        aliases = {
            'vs code': 'visual studio code',
            'vscode': 'visual studio code',
            'visual studio': 'visual studio code',
            'ms edge': 'microsoft edge',
            'edge': 'microsoft edge',
            'chrome': 'google chrome',
        }
        app_name = aliases.get(app_name, app_name)

        process_candidates = self._get_process_candidates(app_name)
        if not process_candidates:
            response = f"I don't know how to close {app_name}"
            self.speak(response)
            return response

        system = platform.system().lower()
        if system == 'windows':
            return self._close_windows_processes(process_candidates, app_name)

        response = f"Closing {app_name} is not supported on this system"
        self.speak(response)
        return response

    def _get_process_candidates(self, app_name: str) -> list:
        """Get possible process names for an app"""
        candidates = []

        app_key = app_name.strip().lower()
        if app_key in self.APPLICATIONS:
            app_path = self.APPLICATIONS[app_key].get('windows')
            if app_path:
                candidates.append(app_path)

        if app_key and not app_key.endswith('.exe'):
            candidates.append(f"{app_key}.exe")
        candidates.append(app_key)

        extra_map = {
            'whatsapp': ['WhatsApp.exe', 'WhatsApp'],
            'google chrome': ['chrome.exe', 'chrome'],
            'microsoft edge': ['msedge.exe', 'msedge'],
            'visual studio code': ['code.exe', 'Code.exe', 'code'],
        }
        candidates.extend(extra_map.get(app_key, []))

        return list(dict.fromkeys([c for c in candidates if c]))

    def _close_windows_processes(self, candidates: list, app_name: str) -> str:
        """Close Windows processes by candidate names"""
        last_error = None
        for proc in candidates:
            try:
                result = subprocess.run(
                    ['taskkill', '/IM', proc, '/F'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    response = f"Closing {app_name}"
                    self.speak(response)
                    return response
                last_error = result.stderr.strip() or result.stdout.strip()
            except Exception as e:
                last_error = str(e)

        response = f"Could not close {app_name}. {last_error or 'Please close it manually.'}"
        self.speak(response)
        return response
