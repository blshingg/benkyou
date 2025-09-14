import os
import csv
import time
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QScrollArea, QHBoxLayout, QLineEdit, QApplication
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer

from spaced_repetition.card import Card
from spaced_repetition.card_data import CardData
from utils.fuzzy_match import fuzzy_match
import translation.romaji_to_kana as romkan

class WordDisplayWidget(QWidget):
    LEVEL_COLORS = {
        0: "#808080",  # Gray
        1: "#ADAD85",  # Yellow-Gray
        2: "#FFFF00",  # Yellow
        3: "#00FF00",  # Green
        4: "#0000FF",  # Blue
    }
    LEVEL_TEXTS = {
        0: "Unknown",
        1: "Familiar",
        2: "Learned",
        3: "Skilled",
        4: "Master",
    }

    def __init__(self, word_data):
        super().__init__()
        self.word_data = word_data
        self.is_pulsing = False
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._toggle_pulse)
        self.pulse_state = False

        self.setContentsMargins(5, 5, 5, 5)
        self.setStyleSheet("border: 1px solid lightgray; border-radius: 5px; background-color: white; color: black;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        japanese_label = QLabel(word_data.japanese)
        japanese_font = QFont("Times New Roman", 18, QFont.Weight.Bold)
        japanese_label.setFont(japanese_font)
        layout.addWidget(japanese_label)

        reading_label = QLabel(word_data.reading)
        reading_font = QFont("Times New Roman", 14)
        reading_label.setFont(reading_font)
        layout.addWidget(reading_label)

        english_label = QLabel(word_data.english)
        english_font = QFont("Times New Roman", 14)
        english_label.setFont(english_font)
        layout.addWidget(english_label)

        # Level display
        level_layout = QHBoxLayout()
        level_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        level = word_data.level
        for i in range(4):
            level_indicator = QLabel()
            level_indicator.setFixedSize(15, 15)
            if i <= level:
                color = self.LEVEL_COLORS.get(level, "#FFFFFF") # Use the actual level's color
                level_indicator.setStyleSheet(f"background-color: {color}; border: 1px solid gray; border-radius: 7px;")
            else:
                level_indicator.setStyleSheet("background-color: lightgray; border: 1px solid gray; border-radius: 7px;")
            level_layout.addWidget(level_indicator)
        
        level_text_label = QLabel(self.LEVEL_TEXTS.get(level, "Unknown"))
        level_text_label.setFont(QFont("Times New Roman", 12))
        level_layout.addWidget(level_text_label)

        layout.addLayout(level_layout)

    def set_pulsing(self, enable):
        if enable and not self.is_pulsing:
            self.is_pulsing = True
            self.pulse_timer.start(500) # Toggle every 500ms
        elif not enable and self.is_pulsing:
            self.is_pulsing = False
            self.pulse_timer.stop()
            self.setStyleSheet("border: 1px solid lightgray; border-radius: 5px; background-color: white; color: black;")

    def _toggle_pulse(self):
        if self.pulse_state:
            self.setStyleSheet("border: 1px solid lightgray; border-radius: 5px; background-color: white; color: black;")
        else:
            self.setStyleSheet("border: 1px solid lightgray; border-radius: 5px; background-color: #FFFACD; color: black;") # Lemon Chiffon
        self.pulse_state = not self.pulse_state

class ProgressWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Progress Overview")
        font = QFont("Times New Roman", 36, QFont.Weight.Bold)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Loading label
        self.loading_label = QLabel("Loading...")
        self.loading_label.setFont(QFont("Times New Roman", 24, QFont.Weight.Bold))
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide() # Hidden by default
        main_layout.addWidget(self.loading_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search cards...")
        self.search_input.textChanged.connect(self._filter_cards)
        main_layout.addWidget(self.search_input)

        # Statistics display
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Times New Roman", 14))
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.stats_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.words_layout = QVBoxLayout(content_widget)
        self.words_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(content_widget)
        main_layout.addWidget(self.scroll_area)

        back_button = QPushButton("Back")
        back_button.setObjectName('back_button')
        back_button.clicked.connect(back_callback)
        main_layout.addWidget(back_button)

        self.all_loaded_word_data = [] # Store all loaded word data
        self.all_word_widgets = [] # Store all WordDisplayWidget instances

    def load_deck(self, deck_path):
        # Show loading indicator
        self.loading_label.show()
        self.search_input.hide()
        self.stats_label.hide()
        self.scroll_area.hide()
        QApplication.processEvents() # Process events to update UI

        # Clear existing widgets
        for widget in self.all_word_widgets:
            widget.deleteLater()
        self.all_word_widgets = []
        self.all_loaded_word_data = []

        deck_name = os.path.splitext(os.path.basename(deck_path))[0]
        progress_files_path = os.path.join(os.path.dirname(__file__), '..', '..', 'progress_files')
        deck_json_path = os.path.join(progress_files_path, f"{deck_name}.json")

        all_cards = []
        progress_data = {}
        if os.path.exists(deck_json_path):
            with open(deck_json_path, 'r', encoding='utf-8') as f:
                progress_list = json.load(f)
                progress_data = {item['japanese']: item for item in progress_list}

        with open(deck_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    japanese, reading, english = row
                    card_data_from_progress = progress_data.get(japanese)
                    if card_data_from_progress:
                        card = Card.from_dict(card_data_from_progress["card"])
                        level = card.level
                        last_reviewed = card_data_from_progress.get("last_reviewed_time")
                    else:
                        card = Card()
                        level = 0
                        last_reviewed = None
                    
                    word_data = CardData(card=card, japanese=japanese, english=english, reading=reading, level=level, last_reviewed_time=last_reviewed)
                    all_cards.append(word_data)
        
        current_timestamp = time.time()
        
        total_cards = len(all_cards)
        learned_cards = 0
        due_cards = 0
        level_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for word_data in all_cards:
            word_display_widget = WordDisplayWidget(word_data)
            
            card = word_data.card
            last_reviewed = word_data.last_reviewed_time

            is_due = False
            if card.status == "learning" and card.step == 0: # New card, unlearned
                is_due = True
            elif last_reviewed is not None and card.interval is not None:
                due_time = last_reviewed + card.interval.total_seconds()
                if current_timestamp >= due_time:
                    is_due = True
            
            if is_due:
                word_display_widget.set_pulsing(True)
                due_cards += 1
            
            self.all_loaded_word_data.append(word_data)
            self.all_word_widgets.append(word_display_widget)
            self.words_layout.addWidget(word_display_widget)

            # Update statistics
            level = word_data.level
            if level == 3:
                learned_cards += 1
            if level == -1:
                level = max(level_distribution.keys())
            level_distribution[level] += 1
        
        stats_text = f"Total Cards: {total_cards}\n"
        stats_text += f"Learned Cards: {learned_cards}\n"
        stats_text += f"Cards Due: {due_cards}\n"
        stats_text += "Level Distribution:\n"
        for level, count in level_distribution.items():
            stats_text += f"  Level {level} ({WordDisplayWidget.LEVEL_TEXTS.get(level, 'Unknown')}): {count}\n"
        
        self.stats_label.setText(stats_text)

        # Hide loading indicator and show content
        self.loading_label.hide()
        self.search_input.show()
        self.stats_label.show()
        self.scroll_area.show()
        QApplication.processEvents() # Process events to update UI

    def _filter_cards(self, query):
        for i, word_data in enumerate(self.all_loaded_word_data):
            word_widget = self.all_word_widgets[i]
            
            japanese = word_data.japanese
            reading = word_data.reading
            english = word_data.english

            if fuzzy_match(query, japanese) or \
               fuzzy_match(query, reading) or \
               fuzzy_match(query, english) or \
               fuzzy_match(romkan.to_kana(query), reading) or \
               fuzzy_match(romkan.to_hiragana(query), reading):
                word_widget.show()
            else:
                word_widget.hide()