"""
Task Executor
Executes tasks using available skills
"""

from typing import Optional, Callable, List
from datetime import datetime
from .task_manager import Task, TaskStatus, TaskQueue


class TaskExecutor:
    """Executes tasks using available skills"""
    
    def __init__(self, jarvis_instance):
        """Initialize executor with Jarvis instance"""
        self.jarvis = jarvis_instance
        self.skills: List = []  # List of skill instances
        self.execution_history: List[Task] = []
    
    def register_skill(self, skill):
        """Register a skill"""
        self.skills.append(skill)
    
    def register_skills(self, skills: List):
        """Register multiple skills"""
        self.skills.extend(skills)
    
    def execute_task(self, task: Task) -> Optional[str]:
        """Execute a single task"""
        task.mark_running()
        try:
            self.jarvis.last_task_command = task.command
        except Exception:
            pass
        
        try:
            # Find matching skill
            for skill in self.skills:
                if skill.can_handle(task.command):
                    result = skill.execute(task.command)
                    task.mark_completed(result)
                    self.execution_history.append(task)
                    return result
            
            # No matching skill found
            raise ValueError(f"No skill found to handle: {task.command}")
            
        except Exception as e:
            task.mark_failed(str(e))
            self.execution_history.append(task)
            self.jarvis.speak(f"Error executing task: {e}")
            return None
    
    def execute_queue(self, task_queue: TaskQueue, stop_on_error: bool = False) -> List[Task]:
        """Execute all tasks in queue"""
        results = []
        
        while True:
            task = task_queue.get_next_task()
            if not task:
                break
            
            result = self.execute_task(task)
            results.append(task)
            
            if stop_on_error and task.status == TaskStatus.FAILED:
                break
        
        return results
    
    def get_execution_history(self) -> List[Task]:
        """Get execution history"""
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
