
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ProgressWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Progress Screen (Not Implemented)")
        font = QFont("Times New Roman", 24)
        label.setFont(font)
        layout.addWidget(label)
        
        back_button = QPushButton("Back")
        back_button.clicked.connect(back_callback)
        layout.addWidget(back_button)
