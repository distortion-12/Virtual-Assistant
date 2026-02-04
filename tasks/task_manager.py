"""
Task Management System
Manages task execution and planning
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents a single task"""
    
    def __init__(self, 
                 task_id: str,
                 command: str,
                 priority: int = 0,
                 description: str = ""):
        self.id = task_id
        self.command = command
        self.priority = priority
        self.description = description
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
    
    def __repr__(self):
        return f"<Task {self.id}: {self.command} [{self.status.value}]>"
    
    def mark_running(self):
        """Mark task as running"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self, result=None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def get_duration(self) -> float:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0


class TaskQueue:
    """Task queue for managing multiple tasks"""
    
    def __init__(self, max_size: int = 100):
        self.tasks: List[Task] = []
        self.max_size = max_size
        self.task_map: Dict[str, Task] = {}
    
    def add_task(self, task: Task) -> bool:
        """Add a task to queue"""
        if len(self.tasks) >= self.max_size:
            return False
        
        self.tasks.append(task)
        self.task_map[task.id] = task
        # Sort by priority
        self.tasks.sort(key=lambda x: x.priority, reverse=True)
        return True
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task from queue"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.task_map.get(task_id)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from queue"""
        if task_id in self.task_map:
            task = self.task_map[task_id]
            self.tasks.remove(task)
            del self.task_map[task_id]
            return True
        return False
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [t for t in self.tasks if t.status == TaskStatus.COMPLETED]
    
    def clear(self):
        """Clear all tasks"""
        self.tasks.clear()
        self.task_map.clear()
