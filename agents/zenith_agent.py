"""
ZENITH Agent
Agentic system for handling complex requests
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum


class AgentState(Enum):
    """Agent state"""
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


class ZenithAgent:
    """Intelligent agent for handling complex requests"""
    
    def __init__(self, jarvis_instance, task_executor, task_planner):
        """Initialize agent"""
        self.jarvis = jarvis_instance
        self.executor = task_executor
        self.planner = task_planner
        self.state = AgentState.IDLE
        self.current_request = None
        self.execution_log: List[Dict[str, Any]] = []
        self.decision_history: List[Dict[str, Any]] = []
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process a user request and return results"""
        self.current_request = request
        try:
            self.jarvis.last_request = request
        except Exception:
            pass
        self.state = AgentState.THINKING
        
        # Log the request
        self._log_action(f"Received request: {request}")
        
        try:
            # Step 1: Plan the request
            self.state = AgentState.PLANNING
            tasks = self.planner.parse_request(request)
            self._log_action(f"Planned {len(tasks)} task(s)")
            
            # Step 2: Execute tasks
            self.state = AgentState.EXECUTING
            results = self._execute_tasks(tasks)
            
            # Step 3: Compile results
            self.state = AgentState.COMPLETED
            response = self._compile_response(tasks, results)
            
            return {
                'success': True,
                'request': request,
                'tasks_count': len(tasks),
                'response': response,
                'execution_log': self.execution_log
            }
            
        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = str(e)
            self._log_action(f"Error: {error_msg}")
            self.jarvis.speak(f"An error occurred: {error_msg}")
            
            return {
                'success': False,
                'request': request,
                'error': error_msg,
                'execution_log': self.execution_log
            }
    
    def _execute_tasks(self, tasks: List) -> List[str]:
        """Execute a list of tasks"""
        results = []
        
        for task in tasks:
            try:
                self._log_action(f"Executing task: {task.command}")
                result = self.executor.execute_task(task)
                results.append(result or "")
                self._log_action(f"Task completed: {task.id}")
            except Exception as e:
                error = str(e)
                results.append(f"Error: {error}")
                self._log_action(f"Task failed: {error}")
        
        return results
    
    def _compile_response(self, tasks: List, results: List[str]) -> str:
        """Compile final response from task results"""
        if not results:
            return "No tasks were executed."

        def _summarize(task, result):
            request = (self.current_request or "").lower()
            question_words = ["who", "what", "why", "how", "when", "where"]
            query_phrases = [
                "tell me", "explain", "define", "information about", "details about",
                "what is", "who is", "how to", "how do", "why is", "why do",
            ]
            is_question = any(word in request for word in question_words)
            is_query = any(phrase in request for phrase in query_phrases)
            normalized_result = (result or "").strip().lower()
            if normalized_result and any(word in normalized_result for word in ["error", "failed", "could not", "not installed", "not available"]):
                return result
            if any(phrase in request for phrase in [
                "not ", "not sent", "wasn't sent", "was not sent", "didn't send", "failed", "not done"
            ]):
                return "Okay"
            if is_question or is_query:
                return result or "I'm not sure, but I can look it up if you want."
            if normalized_result and "attempted" in normalized_result:
                return result
            return f"Done {task.command}"
        
        if len(results) == 1:
            return _summarize(tasks[0], results[0])
        
        # Multiple results
        response = "I've completed the following tasks:\n"
        for i, (task, result) in enumerate(zip(tasks, results), 1):
            response += f"{i}. {_summarize(task, result)}\n"
        
        return response.strip()
    
    def _log_action(self, action: str):
        """Log an action"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'state': self.state.value
        }
        self.execution_log.append(log_entry)
        print(f"[{timestamp}] {action}")
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log"""
        return self.execution_log
    
    def clear_log(self):
        """Clear execution log"""
        self.execution_log.clear()
    
    def get_state(self) -> str:
        """Get current agent state"""
        return self.state.value
