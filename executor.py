#!/usr/bin/env python3
"""
JARVIS Agent Executor
Main entry point for running JARVIS with skills, tasks, and agents
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis import Jarvis
from skills import (
    TimeAndDateSkill,
    ApplicationSkill,
    SystemSkill,
    WebSkill,
    FileSkill,
    WeatherSkill,
    KnowledgeSkill,
    InputSkill,
    MessageSkill,
)
from tasks import TaskExecutor, TaskPlanner, Task
from agents import JarvisAgent


class JarvisExecutor:
    """Main executor for JARVIS system"""
    
    def __init__(self):
        """Initialize the executor"""
        print("=" * 60)
        print("🤖 JARVIS - Agent-Based Executor")
        print("=" * 60)
        
        # Initialize JARVIS core
        self.jarvis = Jarvis()
        print("✓ JARVIS core initialized")
        
        # Initialize task system
        self.task_executor = TaskExecutor(self.jarvis)
        self.task_planner = TaskPlanner(config=self.jarvis.config)
        print("✓ Task system initialized")
        
        # Register skills
        self._register_skills()
        print("✓ Skills registered")
        
        # Initialize agent
        self.agent = JarvisAgent(self.jarvis, self.task_executor, self.task_planner)
        print("✓ Agent initialized")
        
        print("\n" + "=" * 60)
        print("JARVIS is ready!")
        print("=" * 60 + "\n")
    
    def _register_skills(self):
        """Register all skills"""
        skills = [
            TimeAndDateSkill(self.jarvis),
            ApplicationSkill(self.jarvis),
            SystemSkill(self.jarvis),
            WebSkill(self.jarvis),
            FileSkill(self.jarvis),
            WeatherSkill(self.jarvis),
            InputSkill(self.jarvis),
            MessageSkill(self.jarvis),
            KnowledgeSkill(self.jarvis),
        ]
        
        self.task_executor.register_skills(skills)
    
    def process_voice_command(self, command: str) -> str:
        """Process a voice command through the agent"""
        print(f"\n🎤 You said: {command}")
        result = self.agent.process_request(command)
        
        if result['success']:
            print(f"✓ Completed {result['tasks_count']} task(s)")
            return result['response']
        else:
            print(f"✗ Error: {result['error']}")
            return f"Error: {result['error']}"
    
    def process_text_command(self, command: str) -> str:
        """Process a text command through the agent"""
        return self.process_voice_command(command)
    
    def run_voice_mode(self):
        """Run in voice mode"""
        print("\n🎤 Voice Mode - Say 'quit' to exit\n")
        self.jarvis.speak("Voice mode activated. I'm ready to help!")
        
        while True:
            try:
                command = self.jarvis.listen()
                
                if command:
                    if any(word in command.lower() for word in ['quit', 'exit', 'goodbye']):
                        self.jarvis.speak("Goodbye!")
                        break
                    
                    response = self.process_voice_command(command)
                    print(f"📢 JARVIS: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_text_mode(self):
        """Run in text mode"""
        print("\n⌨️ Text Mode - Type 'quit' to exit\n")
        self.jarvis.speak("Text mode activated. I'm ready to help!")
        
        while True:
            try:
                command = input("You: ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'goodbye']:
                    self.jarvis.speak("Goodbye!")
                    print("Goodbye!")
                    break
                
                response = self.process_text_command(command)
                print(f"JARVIS: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_menu(self):
        """Show main menu"""
        print("\n" + "=" * 60)
        print("JARVIS - Main Menu")
        print("=" * 60)
        print("1. Voice Mode (requires microphone)")
        print("2. Text Mode")
        print("3. GUI Mode")
        print("4. Exit")
        print("=" * 60)
        
        choice = input("Select mode (1-4): ").strip()
        return choice
    
    def run(self):
        """Run the executor"""
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                try:
                    self.run_voice_mode()
                except Exception as e:
                    print(f"Error in voice mode: {e}")
            elif choice == '2':
                try:
                    self.run_text_mode()
                except Exception as e:
                    print(f"Error in text mode: {e}")
            elif choice == '3':
                self._launch_gui()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _launch_gui(self):
        """Launch the GUI"""
        try:
            from jarvis_ui import main
            print("\nLaunching GUI...\n")
            main()
        except Exception as e:
            print(f"Error launching GUI: {e}")
            print("Make sure tkinter is installed")


def main():
    """Main entry point"""
    try:
        executor = JarvisExecutor()
        executor.run()
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
