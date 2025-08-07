import sys
import random
import datetime
import math
from PySide6.QtCore import Qt, QPoint, Signal, Slot, QTimer, QRectF
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QLineEdit, QPushButton, QFrame,
    QTextEdit
)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QFont, QTextOption, QMovie

# --- Panel Widget (No changes from previous version) ---
class PanelWidget(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.title = title
        self.glow_intensity = 100

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        shadow_color = QColor(0, 255, 255, self.glow_intensity)
        painter.setPen(QPen(shadow_color, 10))
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setBrush(Qt.black)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.fillRect(1, 1, self.width() - 2, 24, Qt.black)
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(30, 0, self.width() - 35, 25), Qt.AlignLeft | Qt.AlignVCenter, self.title.upper())
        painter.setBrush(Qt.white)
        painter.drawEllipse(10, 8, 8, 8)
        pen = QPen(QColor(0, 255, 255, 150), 2)
        painter.setPen(pen)
        sz = 15
        painter.drawLine(0, 0, sz, 0); painter.drawLine(0, 0, 0, sz)
        painter.drawLine(self.width(), 0, self.width() - sz, 0); painter.drawLine(self.width(), 0, self.width(), sz)
        painter.drawLine(0, self.height(), sz, self.height()); painter.drawLine(0, self.height(), 0, self.height() - sz)
        painter.drawLine(self.width(), self.height(), self.width() - sz, self.height()); painter.drawLine(self.width(), self.height(), self.width(), self.height() - sz)

# --- Animated Core (No changes from previous version) ---
class AnimatedCore(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("https://i.gifer.com/origin/2b/2be8931a53820249311a27345f657551_w200.gif")
        self.setMovie(self.movie)
        self.movie.start()
        self.set_state("idle")

    def set_state(self, new_state: str):
        speeds = {'idle': 50, 'listening': 150, 'thinking': 200, 'speaking': 100}
        self.movie.setSpeed(speeds.get(new_state, 50))

# --- Conversation Widget (No changes from previous version) ---
class ConversationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.current_lyra_message = ""
        self.target_lyra_message = ""
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self._type_char)
        self.font = QFont("Consolas", 11)

    def add_message(self, text, sender):
        if sender == "user": self.messages.append({"text": text, "sender": sender})
        else:
            if self.target_lyra_message: self.messages.append({"text": self.target_lyra_message, "sender": "lyra"})
            self.target_lyra_message = text
            self.current_lyra_message = ""
            self.typing_timer.start(30)
        if len(self.messages) > 15: self.messages.pop(0)
        self.update()

    def _type_char(self):
        if len(self.current_lyra_message) < len(self.target_lyra_message):
            self.current_lyra_message += self.target_lyra_message[len(self.current_lyra_message)]
            self.update()
        else:
            self.typing_timer.stop()
            self.messages.append({"text": self.target_lyra_message, "sender": "lyra"})
            self.target_lyra_message = ""
            self.current_lyra_message = ""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font)
        painter.setPen(Qt.white)
        y_offset, padding = self.height() - 10, 8
        all_messages = self.messages + [{"text": self.current_lyra_message, "sender": "lyra"}]
        for msg in reversed(all_messages):
            if not msg["text"]: continue
            option = QTextOption(Qt.AlignLeft | Qt.AlignVCenter)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            max_width = self.width() - padding * 2
            bounding_rect = painter.boundingRect(QRectF(0, 0, max_width, 1000), msg["text"], option)
            text_height = bounding_rect.height()
            y_offset -= (text_height + padding)
            if y_offset < -text_height: break
            if msg["sender"] == "lyra": painter.drawText(QRectF(padding, y_offset, max_width, text_height), msg["text"], option)
            else:
                option.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                painter.drawText(QRectF(padding, y_offset, max_width, text_height), msg["text"], option)
            y_offset -= padding

# --- Main GUI Window (Updated with Custom Title Bar) ---
class JarvisGUI(QMainWindow):
    text_command_entered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LYRA")
        self.setGeometry(100, 100, 1200, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = self.pos()
        self.background_frame = QFrame(self)
        self.background_frame.setGeometry(0, 0, 1200, 720)
        self.background_frame.setStyleSheet("background-color: transparent;")

        self.stars = [(random.randint(0, 1200), random.randint(0, 720), random.randint(1, 3)) for _ in range(200)]
        self.animation_phase = 0
        self.scanline_y = 0
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self._update_animations)
        self.bg_timer.start(50)
        
        # --- NEW: Custom Title Bar ---
        self.title_bar = QFrame(self.background_frame)
        self.title_bar.setGeometry(0, 0, 1200, 40)
        self.title_bar.setStyleSheet("background-color: transparent;")

        self.title_label = QLabel("Distortion AI Assistant", self.title_bar)
        self.title_label.setGeometry(10, 5, 300, 30)
        self.title_label.setStyleSheet("color: #64FFDA; font-family: 'Consolas'; font-size: 16px; font-weight: bold;")

        button_style = """
            QPushButton {{
                background-color: transparent; color: white; font-size: 16px; border: none;
                font-family: 'Segoe UI Symbol';
            }}
            QPushButton:hover {{ color: #64FFDA; }}
        """
        self.btn_minimize = QPushButton("—", self.title_bar)
        self.btn_minimize.setGeometry(1090, 5, 30, 30)
        self.btn_minimize.setStyleSheet(button_style)
        self.btn_minimize.clicked.connect(self.showMinimized)

        self.btn_maximize = QPushButton("□", self.title_bar)
        self.btn_maximize.setGeometry(1125, 5, 30, 30)
        self.btn_maximize.setStyleSheet(button_style)
        self.btn_maximize.clicked.connect(self.toggle_maximize)

        self.btn_close = QPushButton("✕", self.title_bar)
        self.btn_close.setGeometry(1160, 5, 30, 30)
        self.btn_close.setStyleSheet(button_style)
        self.btn_close.clicked.connect(self.close)

        # --- Layout Panels (Adjusted for Title Bar) ---
        top_margin = 50
        self.chat_panel = PanelWidget("Chat Panel", self.background_frame)
        self.chat_panel.setGeometry(880, top_margin, 300, 650)
        self.todo_panel = PanelWidget("To-Do", self.background_frame)
        self.todo_panel.setGeometry(20, top_margin, 550, 300)
        self.personal_panel = PanelWidget("Personal", self.background_frame)
        self.personal_panel.setGeometry(20, 370, 260, 330)
        self.notes_panel = PanelWidget("Notes", self.background_frame)
        self.notes_panel.setGeometry(300, 370, 270, 330)
        self.core = AnimatedCore(self.background_frame)
        self.core.setGeometry(620, 250, 220, 220)
        self.all_panels = [self.chat_panel, self.todo_panel, self.personal_panel, self.notes_panel]

        # --- Content for Panels ---
        self.conversation_log = ConversationWidget(self.chat_panel)
        self.conversation_log.setGeometry(10, 30, 280, 610)
        self.command_input = QLineEdit(self.background_frame)
        self.command_input.setGeometry(600, 660, 260, 40)
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.setStyleSheet("background-color: black; border: 1px solid white; color: white; padding-left: 10px; font-family: 'Consolas';")
        self.command_input.returnPressed.connect(self.handle_text_command)
        
        self.todo_text_edit = QTextEdit(self.todo_panel)
        self.todo_text_edit.setGeometry(10, 30, 530, 260)
        self.todo_text_edit.setStyleSheet("background-color: black; color: white; border: none; font-family: 'Consolas';")
        self.todo_text_edit.setPlaceholderText("1. \n2. \n3. ")

        self.notes_text_edit = QTextEdit(self.notes_panel)
        self.notes_text_edit.setGeometry(10, 30, 250, 290)
        self.notes_text_edit.setStyleSheet("background-color: black; color: white; border: none; font-family: 'Consolas';")
        self.notes_text_edit.setPlaceholderText("Scratchpad...")

        self.status_label = QLabel("STATUS: STANDBY", self.personal_panel)
        self.status_label.setGeometry(10, 30, 240, 20)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-family: 'Consolas'; font-size: 14px;")

        self.clock_label = QLabel("", self.personal_panel)
        self.clock_label.setGeometry(10, 60, 240, 40)
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("color: #64FFDA; font-family: 'Consolas'; font-size: 28px; font-weight: bold;")
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        self.clock_label.setText(datetime.datetime.now().strftime("%H:%M:%S"))

    def _update_animations(self):
        self.animation_phase += 1
        self.stars = [(x, (y + speed) % 720, speed) for x, y, speed in self.stars]
        self.scanline_y = (self.scanline_y + 2) % self.height()
        glow = int(100 + 30 * math.sin(self.animation_phase * 0.1))
        for panel in self.all_panels:
            panel.glow_intensity = glow
            panel.update()
        self.background_frame.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.black)
        for x, y, speed in self.stars:
            alpha = 50 * speed
            painter.setPen(QColor(255, 255, 255, alpha))
            painter.drawPoint(x, y)
        scanline_color = QColor(0, 255, 255, 50)
        painter.setPen(QPen(scanline_color, 2))
        painter.drawLine(0, self.scanline_y, self.width(), self.scanline_y)

    @Slot(str)
    def update_orb_state(self, state): self.core.set_state(state)
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        # Allow dragging only from the title bar area
        if self.title_bar.geometry().contains(event.pos()):
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event): self.old_pos = None

    def handle_text_command(self):
        command = self.command_input.text()
        if command:
            self.text_command_entered.emit(command)
            self.command_input.clear()

    def update_conversation(self, text):
        try:
            sender, message = text.split(":", 1)
            if "LYRA" in sender.upper(): self.conversation_log.add_message(message.strip(), "lyra")
            else: self.conversation_log.add_message(message.strip(), "user")
        except ValueError:
            self.conversation_log.add_message(text, "lyra")

    def update_status(self, text):
        self.status_label.setText(f"STATUS: {text.upper()}")