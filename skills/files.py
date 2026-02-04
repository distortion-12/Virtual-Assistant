"""
File Operations Skill
Handles file and folder creation/manipulation
"""

from pathlib import Path
from typing import Optional
from .base_skill import BaseSkill, SkillResult


class FileSkill(BaseSkill):
    """Skill for file operations"""
    
    def can_handle(self, command: str) -> bool:
        """Check if command is about file operations"""
        file_keywords = ['file', 'folder', 'directory', 'create', 'screenshot']
        return any(keyword in command.lower() for keyword in file_keywords)
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute file operation command"""
        cmd = command.lower()
        
        try:
            if ('create' in cmd and 'file' in cmd) or 'create file' in cmd:
                filename, target_dir = self._parse_target_path(
                    cmd,
                    'create file', 'create a file', 'create new file', 'create a new file',
                    'create', 'new', 'a', 'an', 'the', 'file', 'text', 'txt'
                )
                return self.create_file(filename, target_dir)
            elif ('create' in cmd and 'folder' in cmd) or ('create' in cmd and 'directory' in cmd):
                foldername, target_dir = self._parse_target_path(
                    cmd,
                    'create folder', 'create directory', 'create a folder', 'create a directory',
                    'create new folder', 'create a new folder',
                    'create', 'new', 'a', 'an', 'the', 'folder', 'directory'
                )
                return self.create_folder(foldername, target_dir)
            elif 'screenshot' in cmd:
                return self.take_screenshot()
        except Exception as e:
            self.log(f"Error: {e}")
            return f"Error: {e}"
    
    def create_file(self, filename: str, target_dir: Optional[Path] = None) -> str:
        """Create a new file"""
        try:
            if not filename:
                filename = "new_file.txt"

            path = Path(filename)
            if target_dir:
                path = target_dir / path.name

            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
            response = f"File {path} created successfully"
            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not create file {filename}: {e}"
            self.speak(response)
            return response
    
    def create_folder(self, foldername: str, target_dir: Optional[Path] = None) -> str:
        """Create a new folder"""
        try:
            if not foldername:
                foldername = "new_folder"

            path = Path(foldername)
            if target_dir:
                path = target_dir / path.name

            path.mkdir(parents=True, exist_ok=True)
            response = f"Folder {path} created successfully"
            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not create folder {foldername}: {e}"
            self.speak(response)
            return response

    def _parse_target_path(self, cmd: str, *keywords: str) -> tuple:
        """Parse filename/foldername and target directory from command."""
        text = cmd
        for kw in keywords:
            text = text.replace(kw, '')
        text = text.strip()

        target_dir = None
        if 'desktop' in text:
            target_dir = Path.home() / 'Desktop'
            text = text.replace('on desktop', '')
            text = text.replace('in desktop', '')
            text = text.replace('desktop', '')

        filename = text.strip()

        if 'txt file' in filename or 'text file' in filename:
            filename = filename.replace('txt file', '').replace('text file', '').strip()
            if not filename:
                filename = 'new_file.txt'
            elif not filename.endswith('.txt'):
                filename = f"{filename}.txt"

        if filename == 'txt' or filename == 'text':
            filename = 'new_file.txt'

        return filename, target_dir
    
    def take_screenshot(self) -> str:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            
            response = f"Screenshot saved as {filename}"
            self.speak(response)
            return response
        except ImportError:
            response = "Screenshot feature requires pyautogui. Please install it."
            self.speak(response)
            return response
        except Exception as e:
            response = f"Could not take screenshot: {e}"
            self.speak(response)
            return response
