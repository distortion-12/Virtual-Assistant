"""
System Control Skill
Handles system information and control
"""

from typing import Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .base_skill import BaseSkill, SkillResult


class SystemSkill(BaseSkill):
    """Skill for system control and monitoring"""
    
    def can_handle(self, command: str) -> bool:
        """Check if command is about system"""
        system_keywords = ['system', 'cpu', 'memory', 'process', 'task manager', 'shutdown', 'restart', 'sleep']
        return any(keyword in command.lower() for keyword in system_keywords)
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute system command"""
        cmd = command.lower()
        
        try:
            if any(word in cmd for word in ['system info', 'system status', 'system information', 'cpu']):
                return self.get_system_info()
            elif any(word in cmd for word in ['running processes', 'task manager', 'processes']):
                return self.list_running_processes()
            elif 'shutdown' in cmd:
                return self.handle_shutdown()
            elif 'restart' in cmd:
                return self.handle_restart()
            elif 'sleep' in cmd or 'hibernate' in cmd:
                return self.handle_sleep()
        except Exception as e:
            self.log(f"Error: {e}")
            return f"Error: {e}"
    
    def get_system_info(self) -> str:
        """Get system information"""
        if not PSUTIL_AVAILABLE:
            response = "System monitoring not available. Please install psutil."
            self.speak(response)
            return response
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = f"CPU usage is {cpu_percent} percent. Memory usage is {memory.percent} percent. Disk usage is {disk.percent} percent."
            self.speak(info)
            return info
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def list_running_processes(self) -> str:
        """List top running processes"""
        if not PSUTIL_AVAILABLE:
            response = "Process monitoring not available."
            self.speak(response)
            return response
        
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            top_5 = processes[:5]
            
            response = "Top 5 processes by CPU usage: "
            for proc in top_5:
                response += f"{proc['name']} ({proc['cpu_percent']}%), "
            
            self.speak("Top 5 processes by CPU usage")
            return response.rstrip(', ')
        except Exception as e:
            return f"Error listing processes: {e}"
    
    def handle_shutdown(self) -> str:
        """Handle shutdown request"""
        response = "Shutdown command recognized but requires confirmation for safety"
        self.speak(response)
        return response
    
    def handle_restart(self) -> str:
        """Handle restart request"""
        response = "Restart command recognized but requires confirmation for safety"
        self.speak(response)
        return response
    
    def handle_sleep(self) -> str:
        """Handle sleep request"""
        response = "Sleep command recognized but requires confirmation for safety"
        self.speak(response)
        return response
