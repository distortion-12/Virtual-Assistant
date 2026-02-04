#!/usr/bin/env python3
"""
JARVIS - GUI Interface with Wake Word Detection and Button Control
A voice-controlled personal assistant with a modern UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from pathlib import Path
from datetime import datetime
import os
import sys

# Import the JARVIS class
from jarvis import Jarvis
from tasks import TaskExecutor, TaskPlanner
from agents import JarvisAgent
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

# Optional imports for wake word detection
try:
    import pyaudio
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    print("Warning: Porcupine wake word detection not available. Install with: pip install pvporcupine pyaudio")


class JarvisUI:
    """JARVIS GUI Interface"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - Voice Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg="#05070f")
        self.root.minsize(900, 700)
        
        # Initialize Jarvis
        self.jarvis = Jarvis()

        # Optional agent pipeline for better intent understanding
        self.use_agent = bool(self.jarvis.config.get("use_agent_in_gui", False))
        self.agent = None
        if self.use_agent:
            self.task_executor = TaskExecutor(self.jarvis)
            self.task_planner = TaskPlanner(config=self.jarvis.config)
            self._register_skills()
            self.agent = JarvisAgent(self.jarvis, self.task_executor, self.task_planner)
        
        # Thread control
        self.listening = False
        self.wake_word_active = False
        self.listen_thread = None
        self.wake_word_thread = None
        
        # Wake word configuration
        self.wake_word = self.jarvis.config.get("wake_word", "jarvis").lower()
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.porcupine_key = (
            self.jarvis.config.get("picovoice_access_key", "")
            or os.getenv("PICOVOICE_ACCESS_KEY", "")
        )
        
        # Setup UI
        self.setup_ui()
        self.add_log("JARVIS initialized successfully!")
        self.add_log(f"Wake word set to: '{self.wake_word}'")
        
    def setup_ui(self):
        """Setup the UI components"""
        # Main container
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Jarvis.Horizontal.TProgressbar",
            troughcolor="#0b1120",
            bordercolor="#0b1120",
            background="#4de1ff",
            lightcolor="#4de1ff",
            darkcolor="#4de1ff",
        )

        main_frame = tk.Frame(self.root, bg="#05070f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # ===== HEADER =====
        header_frame = tk.Frame(main_frame, bg="#08101f")
        header_frame.pack(fill=tk.X, pady=(0, 12))

        title_block = tk.Frame(header_frame, bg="#08101f")
        title_block.pack(side=tk.LEFT, padx=12, pady=12)

        title_label = tk.Label(
            title_block,
            text="J A R V I S",
            font=("Segoe UI", 24, "bold"),
            bg="#08101f",
            fg="#4de1ff"
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = tk.Label(
            title_block,
            text="Personal Assistant Interface",
            font=("Segoe UI", 10),
            bg="#08101f",
            fg="#7aa2f7"
        )
        subtitle_label.pack(anchor=tk.W)

        self.clock_label = tk.Label(
            header_frame,
            text="--:--:--",
            font=("Segoe UI", 14, "bold"),
            bg="#08101f",
            fg="#9ee7ff"
        )
        self.clock_label.pack(side=tk.RIGHT, padx=16)

        self.status_label = tk.Label(
            header_frame,
            text="READY",
            font=("Segoe UI", 10, "bold"),
            bg="#08101f",
            fg="#4de1ff"
        )
        self.status_label.pack(side=tk.RIGHT, padx=12)

        accent_line = tk.Frame(header_frame, bg="#1a3a5e", height=2)
        accent_line.pack(fill=tk.X, side=tk.BOTTOM)

        # ===== BODY =====
        body_frame = tk.Frame(main_frame, bg="#05070f")
        body_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(body_frame, bg="#0b1224")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        right_panel = tk.Frame(body_frame, bg="#0b1224", width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # ===== RESPONSE + LOG =====
        response_label = tk.Label(
            left_panel,
            text="RESPONSE",
            font=("Segoe UI", 9, "bold"),
            bg="#0b1224",
            fg="#4de1ff"
        )
        response_label.pack(anchor=tk.W, padx=12, pady=(12, 6))

        self.response_display = scrolledtext.ScrolledText(
            left_panel,
            height=5,
            bg="#0b1126",
            fg="#7CFFB2",
            font=("Cascadia Mono", 10),
            relief=tk.FLAT,
            bd=0,
            insertbackground="#4de1ff"
        )
        self.response_display.pack(fill=tk.X, expand=False, padx=12, pady=(0, 10))

        log_label = tk.Label(
            left_panel,
            text="SYSTEM LOG",
            font=("Segoe UI", 9, "bold"),
            bg="#0b1224",
            fg="#4de1ff"
        )
        log_label.pack(anchor=tk.W, padx=12, pady=(6, 6))

        self.log_display = scrolledtext.ScrolledText(
            left_panel,
            height=12,
            bg="#0b1126",
            fg="#b2b9d1",
            font=("Cascadia Mono", 9),
            relief=tk.FLAT,
            bd=0,
            insertbackground="#4de1ff"
        )
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # ===== CONTROLS =====
        button_frame = tk.Frame(left_panel, bg="#0b1224")
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.wake_word_btn = tk.Button(
            button_frame,
            text="WAKE WORD",
            command=self.toggle_wake_word_detection,
            bg="#4de1ff",
            fg="#081018",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#2bb6d6",
            activeforeground="#081018"
        )
        self.wake_word_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.listen_btn = tk.Button(
            button_frame,
            text="LISTEN",
            command=self.start_listening,
            bg="#7aa2f7",
            fg="#081018",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#5b7fd1",
            activeforeground="#081018"
        )
        self.listen_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.text_btn = tk.Button(
            button_frame,
            text="TEXT INPUT",
            command=self.get_text_command,
            bg="#ffb86c",
            fg="#081018",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#e39a45",
            activeforeground="#081018"
        )
        self.text_btn.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = tk.Button(
            button_frame,
            text="CLEAR LOG",
            command=self.clear_log,
            bg="#2a335a",
            fg="#c9d1ff",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#3a4576",
            activeforeground="#c9d1ff"
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))

        exit_btn = tk.Button(
            button_frame,
            text="EXIT",
            command=self.exit_app,
            bg="#ff5370",
            fg="#081018",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#d6455d",
            activeforeground="#081018"
        )
        exit_btn.pack(side=tk.RIGHT)

        # ===== HUD PANEL =====
        hud_title = tk.Label(
            right_panel,
            text="CORE STATUS",
            font=("Segoe UI", 9, "bold"),
            bg="#0b1224",
            fg="#4de1ff"
        )
        hud_title.pack(anchor=tk.W, padx=12, pady=(12, 6))

        self.hud_canvas = tk.Canvas(
            right_panel,
            width=280,
            height=280,
            bg="#0b1224",
            highlightthickness=0
        )
        self.hud_canvas.pack(padx=20, pady=(0, 12))

        self.hud_status_label = tk.Label(
            right_panel,
            text="SYSTEM ONLINE",
            font=("Segoe UI", 10, "bold"),
            bg="#0b1224",
            fg="#7CFFB2"
        )
        self.hud_status_label.pack(pady=(0, 12))

        metrics_title = tk.Label(
            right_panel,
            text="SYSTEM METRICS",
            font=("Segoe UI", 9, "bold"),
            bg="#0b1224",
            fg="#4de1ff"
        )
        metrics_title.pack(anchor=tk.W, padx=12, pady=(0, 6))

        metrics_frame = tk.Frame(right_panel, bg="#0b1224")
        metrics_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        for label, value, color in [
            ("VOICE", 78, "#4de1ff"),
            ("NLP", 62, "#7aa2f7"),
            ("SENSORS", 51, "#ffb86c"),
        ]:
            row = tk.Frame(metrics_frame, bg="#0b1224")
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row,
                text=label,
                font=("Segoe UI", 8, "bold"),
                bg="#0b1224",
                fg="#9ee7ff"
            ).pack(side=tk.LEFT)
            bar = ttk.Progressbar(
                row,
                style="Jarvis.Horizontal.TProgressbar",
                orient=tk.HORIZONTAL,
                mode="determinate",
                maximum=100,
                value=value,
                length=160
            )
            bar.pack(side=tk.RIGHT, padx=(8, 0))
            bar.configure(style="Jarvis.Horizontal.TProgressbar")
            style.configure("Jarvis.Horizontal.TProgressbar", background=color)

        info_text = f"Wake word: '{self.wake_word}'"
        info_label = tk.Label(
            right_panel,
            text=info_text,
            font=("Segoe UI", 9),
            bg="#0b1224",
            fg="#6b7aa7"
        )
        info_label.pack(pady=(0, 12))

        self._draw_hud()
        self._animate_hud()
        self._update_clock()

    def _draw_hud(self):
        """Draw the static HUD elements."""
        self.hud_canvas.delete("all")
        w = int(self.hud_canvas["width"])
        h = int(self.hud_canvas["height"])
        cx, cy = w // 2, h // 2

        # Subtle grid
        for x in range(0, w, 20):
            self.hud_canvas.create_line(x, 0, x, h, fill="#0e1a2f")
        for y in range(0, h, 20):
            self.hud_canvas.create_line(0, y, w, y, fill="#0e1a2f")

        # Outer ring
        self.hud_canvas.create_oval(
            cx - 120,
            cy - 120,
            cx + 120,
            cy + 120,
            outline="#2bb6d6",
            width=2
        )

        # Inner ring
        self.hud_canvas.create_oval(
            cx - 70,
            cy - 70,
            cx + 70,
            cy + 70,
            outline="#7aa2f7",
            width=2
        )

        # Core
        self.core_orb = self.hud_canvas.create_oval(
            cx - 18,
            cy - 18,
            cx + 18,
            cy + 18,
            outline="#7CFFB2",
            width=2
        )

        self.hud_text = self.hud_canvas.create_text(
            cx,
            cy + 42,
            text="READY",
            fill="#9ee7ff",
            font=("Segoe UI", 10, "bold")
        )

        # Rotating arcs
        self.arc_one = self.hud_canvas.create_arc(
            cx - 100,
            cy - 100,
            cx + 100,
            cy + 100,
            start=0,
            extent=60,
            style=tk.ARC,
            outline="#4de1ff",
            width=3
        )
        self.arc_two = self.hud_canvas.create_arc(
            cx - 85,
            cy - 85,
            cx + 85,
            cy + 85,
            start=180,
            extent=50,
            style=tk.ARC,
            outline="#ffb86c",
            width=3
        )

        self.scanline = self.hud_canvas.create_line(
            0,
            0,
            w,
            0,
            fill="#4de1ff",
            width=2
        )
        self.scanline_pos = 0

        self.arc_angle = 0

    def _animate_hud(self):
        """Animate HUD arcs for a live Jarvis feel."""
        self.arc_angle = (self.arc_angle + 4) % 360
        self.hud_canvas.itemconfigure(self.arc_one, start=self.arc_angle)
        self.hud_canvas.itemconfigure(self.arc_two, start=(180 - self.arc_angle) % 360)
        self.scanline_pos = (self.scanline_pos + 3) % int(self.hud_canvas["height"])
        self.hud_canvas.coords(
            self.scanline,
            0,
            self.scanline_pos,
            int(self.hud_canvas["width"]),
            self.scanline_pos,
        )
        self.root.after(60, self._animate_hud)

    def _update_clock(self):
        """Update the header clock."""
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self._update_clock)

    def _register_skills(self):
        """Register all skills for agent pipeline"""
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
        
    def add_log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_display.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, log_entry)
        self.log_display.see(tk.END)
        self.log_display.config(state=tk.DISABLED)
        
        # Also print to console
        print(log_entry.strip())
    
    def add_response(self, message):
        """Add message to response display"""
        self.response_display.config(state=tk.NORMAL)
        self.response_display.insert(tk.END, message + "\n")
        self.response_display.see(tk.END)
        self.response_display.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_display.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        self.log_display.config(state=tk.DISABLED)
        self.add_log("Log cleared")
    
    def update_status(self, status, color="#00d4ff"):
        """Update status label"""
        self.status_label.config(text=status, fg=color)
        if hasattr(self, "hud_status_label"):
            self.hud_status_label.config(text=status, fg=color)
        if hasattr(self, "hud_text"):
            self.hud_canvas.itemconfigure(self.hud_text, text=status)
        self.root.update()
    
    def toggle_wake_word_detection(self):
        """Toggle wake word detection on/off"""
        if self.wake_word_active:
            self.stop_wake_word_detection()
        else:
            self.start_wake_word_detection()
    
    def start_wake_word_detection(self):
        """Start listening for wake word"""
        if not PORCUPINE_AVAILABLE:
            self.add_log("❌ Porcupine wake word detection not available")
            self.add_log("Install with: pip install pvporcupine pyaudio")
            messagebox.showwarning(
                "Wake Word Detection",
                "Porcupine not installed.\n\nInstall with:\npip install pvporcupine pyaudio"
            )
            return
        
        self.wake_word_active = True
        self.wake_word_btn.config(
            text="STOP WAKE WORD",
            bg="#ff5370",
            activebackground="#d6455d"
        )
        self.update_status("LISTENING", "#ffb86c")
        self.add_log(f"🎤 Listening for wake word '{self.wake_word}'...")
        
        # Start wake word detection in a separate thread
        self.wake_word_thread = threading.Thread(target=self._wake_word_loop, daemon=True)
        self.wake_word_thread.start()
    
    def _wake_word_loop(self):
        """Loop for wake word detection"""
        try:
            if not self.porcupine_key:
                self.add_log("❌ Picovoice access key not set")
                self.add_log("Add picovoice_access_key to jarvis_config.json")
                self._simple_wake_word_detection()
                return

            # Initialize Porcupine for wake word detection
            self.porcupine = pvporcupine.create(
                access_key=self.porcupine_key,
                keywords=[self.wake_word],
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )

            import struct
            while self.wake_word_active:
                pcm = self.audio_stream.read(
                    self.porcupine.frame_length,
                    exception_on_overflow=False,
                )
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm)
                if result >= 0:
                    self.add_log(f"✅ Wake word detected: '{self.wake_word}'")
                    self.update_status("WAKE DETECTED", "#7CFFB2")
                    self.root.after(100, self.start_listening)
                    self.root.after(800, self._continue_wake_word_detection)
            
        except Exception as e:
            self.add_log(f"❌ Wake word detection error: {e}")
            self.wake_word_active = False
            self.wake_word_btn.config(
                text="WAKE WORD",
                bg="#4de1ff",
                activebackground="#2bb6d6"
            )
            self.update_status("READY", "#4de1ff")
        finally:
            try:
                if self.audio_stream:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                if self.pa:
                    self.pa.terminate()
                if self.porcupine:
                    self.porcupine.delete()
            except Exception:
                pass
    
    def _simple_wake_word_detection(self):
        """Simple wake word detection using speech recognition"""
        if not self.listening and self.wake_word_active:
            try:
                command = self.jarvis.listen()
                if command and self.wake_word in command:
                    self.add_log(f"✅ Wake word detected in: '{command}'")
                    self.update_status("🎤 Wake word detected! Ready for command...", "#4caf50")
                    self.root.after(500, lambda: self._continue_wake_word_detection())
                elif self.wake_word_active:
                    self.root.after(500, lambda: self._simple_wake_word_detection())
            except Exception as e:
                if self.wake_word_active:
                    self.root.after(1000, lambda: self._simple_wake_word_detection())
    
    def _continue_wake_word_detection(self):
        """Continue wake word detection after detection"""
        if self.wake_word_active:
            self.update_status("LISTENING", "#ffb86c")
            self.root.after(1000, lambda: self._simple_wake_word_detection())
    
    def stop_wake_word_detection(self):
        """Stop listening for wake word"""
        self.wake_word_active = False
        self.wake_word_btn.config(
            text="WAKE WORD",
            bg="#4de1ff",
            activebackground="#2bb6d6"
        )
        self.update_status("READY", "#4de1ff")
        self.add_log("🛑 Wake word detection stopped")
    
    def start_listening(self):
        """Start listening for voice command"""
        if self.listening:
            return
        
        self.listening = True
        self.listen_btn.config(state=tk.DISABLED, bg="#444")
        self.update_status("LISTENING", "#ffb86c")
        self.add_log("🔊 Listening for voice command...")
        
        self.listen_thread = threading.Thread(target=self._listen_thread, daemon=True)
        self.listen_thread.start()
    
    def _listen_thread(self):
        """Thread function for listening"""
        try:
            command = self.jarvis.listen()
            self.process_command(command)
        except Exception as e:
            self.add_log(f"❌ Listen error: {e}")
        finally:
            self.listening = False
            self.listen_btn.config(state=tk.NORMAL, bg="#7aa2f7")
            self.update_status("READY", "#4de1ff")
    
    def get_text_command(self):
        """Get command via text input"""
        # Create a simple input dialog
        input_window = tk.Toplevel(self.root)
        input_window.title("Enter Command")
        input_window.geometry("400x150")
        input_window.configure(bg="#1a1f3a")
        
        label = tk.Label(
            input_window,
            text="Enter your command:",
            font=("Arial", 11),
            bg="#1a1f3a",
            fg="#00d4ff"
        )
        label.pack(pady=10)
        
        entry = tk.Entry(
            input_window,
            font=("Arial", 11),
            bg="#0f1428",
            fg="#00ff00",
            insertbackground="#00d4ff"
        )
        entry.pack(padx=10, pady=5, fill=tk.X)
        entry.focus()
        
        def submit():
            command = entry.get().lower()
            input_window.destroy()
            if command:
                self.add_log(f"📝 Text command: {command}")
                self.process_command(command)
        
        submit_btn = tk.Button(
            input_window,
            text="Submit",
            command=submit,
            bg="#00d4ff",
            fg="#000",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        )
        submit_btn.pack(pady=10)
        
        entry.bind("<Return>", lambda e: submit())
    
    def process_command(self, command):
        """Process the command"""
        if not command:
            self.add_log("⚠️ No command recognized")
            return
        
        self.add_log(f"🔍 Processing: '{command}'")
        self.update_status("PROCESSING", "#7aa2f7")
        
        try:
            # Execute the command through Jarvis
            response = self.execute_jarvis_command(command)
            if response:
                self.add_response(response)
            
            # Only log success if response doesn't indicate failure
            if response and ("not installed" not in response.lower() and "not available" not in response.lower()):
                self.add_log("✅ Command executed successfully")
            else:
                self.add_log(f"⚠️ Command completed with result: {response[:50]}...")
        except Exception as e:
            self.add_log(f"❌ Error: {e}")
        
        self.update_status("READY", "#4de1ff")
    
    def execute_jarvis_command(self, command):
        """Execute command through Jarvis"""
        if self.use_agent and self.agent:
            result = self.agent.process_request(command)
            if result.get("success"):
                return result.get("response")
            return f"Error: {result.get('error', 'Unknown error')}"

        response = ""
        
        # Greetings
        if any(word in command for word in ["hello", "hi", "hey", "greetings"]):
            response = "Hello! I'm Jarvis, your personal assistant. How can I help you?"
            self.jarvis.speak(response)
        
        # Time
        elif any(word in command for word in ["time", "what's the time", "current time", "what time"]):
            try:
                response = self.jarvis.get_time()
            except:
                from datetime import datetime
                current_time = datetime.now().strftime("%I:%M %p")
                response = f"The current time is {current_time}"
                self.jarvis.speak(response)
        
        # Date
        elif any(word in command for word in ["date", "today", "what's today"]):
            try:
                response = self.jarvis.get_date()
            except:
                from datetime import datetime
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}"
                self.jarvis.speak(response)
        
        # Open applications
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            
            # Remove common modifiers as whole words only
            words = app_name.split()
            modifiers = ['please', 'can', 'you', 'could', 'will', 'would', 'the', 'a', 'an']
            words = [w for w in words if w.lower() not in modifiers]
            app_name = ' '.join(words).strip()
            
            result = self.jarvis.open_application(app_name)
            response = result if result else f"Attempting to open {app_name}..."

        # Open applications (without saying "open")
        elif command in [
            "whatsapp",
            "telegram",
            "chrome",
            "google chrome",
            "microsoft edge",
            "edge",
            "visual studio code",
            "vs code",
            "vscode",
            "notepad",
            "calculator",
            "spotify",
            "discord",
            "slack",
            "teams",
            "zoom",
            "file explorer",
            "files",
            "browser",
        ]:
            result = self.jarvis.open_application(command)
            response = result if result else f"Attempting to open {command}..."
        
        # Search
        elif "search" in command:
            query = command.replace("search", "").strip()
            response = f"Searching for {query} on the web..."
            self.jarvis.speak(response)
            self.jarvis.search_web(query)
            return response
        
        # Open website
        elif any(word in command for word in ["open youtube", "open google", "open github", "open website"]):
            if "youtube" in command:
                self.jarvis.open_website("youtube.com")
                response = "Opening YouTube"
            elif "google" in command:
                self.jarvis.open_website("google.com")
                response = "Opening Google"
            elif "github" in command:
                self.jarvis.open_website("github.com")
                response = "Opening GitHub"
            else:
                website = command.replace("open", "").replace("website", "").strip()
                self.jarvis.open_website(website)
                response = f"Opening {website}"
            self.jarvis.speak(response)
            return response
        
        # System info
        elif any(word in command for word in ["system info", "system status", "system information", "cpu usage", "running process"]):
            try:
                response = self.jarvis.system_info()
            except:
                response = "System information not available"
                self.jarvis.speak(response)
        
        # Weather
        elif "weather" in command:
            try:
                response = self.jarvis.get_weather()
            except:
                response = "Weather information not available"
                self.jarvis.speak(response)
        
        # General query fallback - search knowledge base first, then web
        else:
            response = f"Let me check that for you: {command}"
            self.jarvis.speak(response)
            # Try to get knowledge-based answer
            answer = self.jarvis.search_knowledge(command)
            if answer:
                return answer
            return (
                f"I couldn't find a concise answer for {command}. "
                "Try rephrasing, or say 'search' followed by your query to open the web."
            )
        
        return response if response else "Command processed"
    
    def exit_app(self):
        """Exit the application"""
        self.stop_wake_word_detection()
        if messagebox.askokcancel("Exit", "Are you sure you want to exit JARVIS?"):
            self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
