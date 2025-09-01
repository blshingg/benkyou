import os
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QGroupBox, QRadioButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class StudyMenuWidget(QWidget):
    def __init__(self, back_callback, study_deck_callback):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Select a Deck")
        font = QFont("Times New Roman", 36, QFont.Weight.Bold)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.vocab_path = os.path.join(os.path.dirname(__file__), '..', '..', 'vocab_files')
        for file_name in os.listdir(self.vocab_path):
            if file_name.endswith('.csv'):
                deck_name = os.path.splitext(file_name)[0]
                button = QPushButton(deck_name)
                button.setObjectName(f'deck_button_{deck_name}')
                button.clicked.connect(lambda checked, f=file_name: self.on_deck_selected(os.path.join(self.vocab_path, f)))
                layout.addWidget(button)

        mode_groupbox = QGroupBox("Quiz Mode")
        mode_layout = QVBoxLayout()
        self.eng_to_jap_radio = QRadioButton("English → Japanese")
        self.eng_to_jap_radio.setObjectName('eng_to_jap_radio')
        self.jap_to_eng_radio = QRadioButton("Japanese → English")
        self.jap_to_eng_radio.setObjectName('jap_to_eng_radio')
        self.mixed_radio = QRadioButton("Mixed")
        self.mixed_radio.setObjectName('mixed_radio')
        self.eng_to_jap_radio.setChecked(True)
        mode_layout.addWidget(self.eng_to_jap_radio)
        mode_layout.addWidget(self.jap_to_eng_radio)
        mode_layout.addWidget(self.mixed_radio)
        mode_groupbox.setLayout(mode_layout)
        layout.addWidget(mode_groupbox)

        back_button = QPushButton("Back")
        back_button.setObjectName('back_button')
        back_button.clicked.connect(back_callback)
        layout.addWidget(back_button)

        self.study_deck_callback = study_deck_callback

    def on_deck_selected(self, deck_path):
        if self.eng_to_jap_radio.isChecked():
            mode = "eng_to_jap"
        elif self.jap_to_eng_radio.isChecked():
            mode = "jap_to_eng"
        else:
            mode = "mixed"
        self.study_deck_callback(deck_path, mode)