"""
Task Planning and Parsing
Breaks down user requests into tasks
"""

import re
from typing import List, Dict, Any, Optional
from .task_manager import Task
from .hosted_intent import HostedIntentRouter


class TaskPlanner:
    """Plans and breaks down requests into tasks"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize task planner"""
        self.task_counter = 0
        self.config = config or {}
        self.intent_router = HostedIntentRouter.from_config(self.config)
    
    def parse_request(self, request: str) -> List[Task]:
        """Parse a user request into tasks"""
        tasks = []
        
        # Split compound requests using conjunctions
        parts = self._split_request(request)
        
        for part in parts:
            normalized = self._normalize_with_intent(part.strip())
            task = self._create_task_from_part(normalized or part.strip())
            if task:
                tasks.append(task)
        
        return tasks
    
    def _split_request(self, request: str) -> List[str]:
        """Split request into parts based on conjunctions"""
        # Split on 'and', 'then', 'also'
        parts = re.split(r'\s+(?:and|then|also|after|plus)\s+', request, flags=re.IGNORECASE)
        return parts
    
    def _create_task_from_part(self, part: str) -> Optional[Task]:
        """Create a task from a request part"""
        if not part:
            return None

        normalized_part = part.strip()
        if normalized_part.lower() in ["send again", "resend"]:
            normalized_part = "send again"
        
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        # Determine priority based on keywords
        priority = self._determine_priority(part)
        
        return Task(
            task_id=task_id,
            command=normalized_part,
            priority=priority,
            description=f"Task: {normalized_part}"
        )

    def _normalize_with_intent(self, part: str) -> Optional[str]:
        """Use hosted intent model to normalize a command"""
        if not self.intent_router:
            return None

        try:
            return self.intent_router.normalize_command(part)
        except Exception:
            return None
    
    def _determine_priority(self, text: str) -> int:
        """Determine task priority"""
        priority = 0
        
        high_priority_keywords = ['urgent', 'important', 'immediately', 'asap', 'critical']
        low_priority_keywords = ['later', 'when you can', 'optional']
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in high_priority_keywords):
            priority = 10
        elif any(keyword in text_lower for keyword in low_priority_keywords):
            priority = -10
        
        return priority
    
    def combine_tasks(self, tasks: List[Task]) -> List[Task]:
        """Combine related tasks if possible"""
        combined = []
        
        # Group tasks by type
        task_groups: Dict[str, List[Task]] = {}
        
        for task in tasks:
            # Extract task type from command
            task_type = self._get_task_type(task.command)
            
            if task_type not in task_groups:
                task_groups[task_type] = []
            task_groups[task_type].append(task)
        
        # Combine similar tasks
        for task_type, group in task_groups.items():
            if len(group) > 1:
                combined.append(self._merge_tasks(group))
            else:
                combined.extend(group)
        
        return combined
    
    def _get_task_type(self, command: str) -> str:
        """Extract task type from command"""
        keywords = {
            'open': ['open', 'launch', 'start'],
            'search': ['search', 'find', 'look'],
            'information': ['time', 'date', 'weather', 'info'],
            'system': ['system', 'cpu', 'memory', 'process'],
        }
        
        cmd_lower = command.lower()
        for task_type, keywords_list in keywords.items():
            if any(kw in cmd_lower for kw in keywords_list):
                return task_type
        
        return 'general'
    
    def _merge_tasks(self, tasks: List[Task]) -> Task:
        """Merge multiple tasks into one"""
        if not tasks:
            return None
        
        merged_command = ' and '.join([t.command for t in tasks])
        merged_task = Task(
            task_id=tasks[0].id,
            command=merged_command,
            priority=max([t.priority for t in tasks]),
            description=f"Merged task: {merged_command}"
        )
        return merged_task


from typing import Optional
