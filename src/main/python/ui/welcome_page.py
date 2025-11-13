from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTextEdit, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect

class IntroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f5f5; color: #1f2937;")
        self.setContentsMargins(15, 15, 15, 15)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        
        # Title with drop shadow
        self.title = QLabel("Welcome to Environmental Monitoring & Control System")
        self.title.setFont(QFont("Arial", 22, QFont.Bold))
        self.title.setStyleSheet("color: #1f2937; padding 10;")
        self.title.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.title)

        # Body text with effect
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
                font-size: 20px;
                color: #111827;
            }
        """)
        self.layout.addWidget(self.info)

        # set layout
        self.setLayout(self.layout)

        # Full text to animate
        self.full_text = """🌿 About the Application:
This system monitors, analyzes, and helps control various environmental factors with differents modules.

🌍 Why This Matters:
- The environment sustains all forms of life.
- Clean air, fresh water, and fertile land are critical for survival.
- Biodiversity ensures ecological balance and resilience.

🌱 How You Can Help:
- Keep surroundings clean.
- Reduce, reuse, and recycle waste.
- Avoid pollution and save water.
- Plant trees and protect green spaces.

🐝 Importance for Ecosystems, as healthy ecosystems support:
- Agriculture & food chains
- Climate regulation
- Natural disaster prevention

Let's protect our planet — together."""

        # Typing effect timer
        self.char_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_char)
        QTimer.singleShot(500, self.timer.start)  # Start after slight delay
        self.timer.setInterval(10)  # Typing speed (ms per char)
        self.layout.addWidget(self.info)
        self.setLayout(self.layout)

        # Start animation after short delay
        QTimer.singleShot(300, self.timer.start)


    def type_next_char(self):
        if self.char_index < len(self.full_text):
            self.info.insertPlainText(self.full_text[self.char_index])
            self.char_index += 1
            self.info.moveCursor(self.info.textCursor().End)
        else:
            self.timer.stop()
