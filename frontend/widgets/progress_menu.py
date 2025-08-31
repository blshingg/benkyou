
import os
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ProgressMenuWidget(QWidget):
    def __init__(self, back_callback, show_progress_for_deck_callback):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Select Deck for Progress")
        font = QFont("Times New Roman", 36, QFont.Weight.Bold)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.vocab_path = os.path.join(os.path.dirname(__file__), '..', '..', 'vocab_files')
        for file_name in os.listdir(self.vocab_path):
            if file_name.endswith('.csv'):
                deck_name = os.path.splitext(file_name)[0]
                button = QPushButton(deck_name)
                button.clicked.connect(lambda checked, f=file_name: show_progress_for_deck_callback(os.path.join(self.vocab_path, f)))
                layout.addWidget(button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(back_callback)
        layout.addWidget(back_button)
