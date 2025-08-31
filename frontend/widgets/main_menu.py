
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MainMenuWidget(QWidget):
    def __init__(self, study_callback, show_progress_menu_callback, quit_callback):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("Welcome to Benkyou")
        font = QFont("Times New Roman", 48, QFont.Weight.Bold)
        welcome_label.setFont(font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        
        study_button = QPushButton("1. Study")
        study_button.setShortcut("1")
        study_button.clicked.connect(study_callback)
        
        progress_button = QPushButton("2. View Progress")
        progress_button.setShortcut("2")
        progress_button.clicked.connect(show_progress_menu_callback)

        quit_button = QPushButton("3. Quit")
        quit_button.setShortcut("3")
        quit_button.clicked.connect(quit_callback)
        
        button_layout.addWidget(study_button)
        button_layout.addWidget(progress_button)
        button_layout.addWidget(quit_button)

        layout.addLayout(button_layout)
