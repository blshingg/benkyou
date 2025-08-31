import csv
import os
import sys
import json
import random
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from spaced_repetition.card import Card
import translation.romaji_to_kana as romkan

class StudySessionWidget(QWidget):
    LEVEL_COLORS = {
        0: "#808080",  # Gray
        1: "#ADAD85",  # Yellow-Gray
        2: "#FFFF00",  # Yellow
        3: "#00FF00",  # Green
    }

    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self.deck = []
        self.current_card_index = 0
        self.deck_path = None
        self.mode = None
        self.current_question_is_japanese = False

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_frame.setLineWidth(3)
        card_layout = QVBoxLayout(self.card_frame)
        
        self.question_label = QLabel("")
        font = QFont("Times New Roman", 36)
        self.question_label.setFont(font)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.question_label)
        layout.addWidget(self.card_frame)

        self.answer_input = QLineEdit()
        self.answer_input.returnPressed.connect(self.check_answer)
        layout.addWidget(self.answer_input)

        self.kana_preview_label = QLabel("")
        font = QFont("Times New Roman", 24)
        self.kana_preview_label.setFont(font)
        self.kana_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.kana_preview_label)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        self.submit_button.setDefault(True)
        layout.addWidget(self.submit_button)

        self.feedback_label = QLabel("")
        font = QFont("Times New Roman", 24)
        self.feedback_label.setFont(font)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.update_card)
        layout.addWidget(self.continue_button)

        self.back_button = QPushButton("Back to Menu")
        self.back_button.clicked.connect(self.back_callback)
        layout.addWidget(self.back_button)

        self.answer_input.textChanged.connect(self.on_text_changed)

    def on_text_changed(self, text):
        if not self.current_question_is_japanese:
            if text.isupper():
                kana = romkan.to_katakana(text)
            else:
                kana = romkan.to_hiragana(text)
            self.kana_preview_label.setText(kana)
        else:
            self.kana_preview_label.setText("")

    def start_study_session(self, deck_path, mode):
        self.deck_path = deck_path
        self.mode = mode
        
        progress_data = self._load_progress()
        
        reviewed_cards = []
        unseen_cards = []

        with open(deck_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    japanese, reading, english = row
                    card_data_from_progress = progress_data.get(japanese)
                    if card_data_from_progress:
                        card = Card.from_dict(card_data_from_progress["card"])
                        level = card_data_from_progress["level"]
                        reviewed_cards.append({"japanese": japanese, "reading": reading, "english": english, "card": card, "level": level})
                    else:
                        card = Card()
                        level = 0
                        unseen_cards.append({"japanese": japanese, "reading": reading, "english": english, "card": card, "level": level})
        
        random.shuffle(reviewed_cards)
        self.deck = reviewed_cards + unseen_cards
        
        self.current_card_index = 0
        self.next_card()

    def next_card(self):
        if self.current_card_index >= len(self.deck):
            self.question_label.setText("Deck finished!")
            self.answer_input.hide()
            self.kana_preview_label.hide()
            self.submit_button.hide()
            self.continue_button.hide()
            self.feedback_label.hide()
            self.card_frame.setStyleSheet("border: none")
            return

        self.answer_input.show()
        self.kana_preview_label.show()
        self.submit_button.show()
        self.submit_button.setDefault(True)
        self.continue_button.hide()
        self.continue_button.setDefault(False)
        self.feedback_label.setText("")
        self.kana_preview_label.setText("")
        self.answer_input.setText("")
        self.answer_input.setFocus()

        card_data = self.deck[self.current_card_index]
        
        if self.mode == "eng_to_jap":
            self.question_label.setText(card_data["english"])
            self.current_question_is_japanese = False
        elif self.mode == "jap_to_eng":
            self.question_label.setText(card_data["japanese"])
            self.current_question_is_japanese = True
        else: # mixed mode
            if random.choice([True, False]):
                self.question_label.setText(card_data["japanese"])
                self.current_question_is_japanese = True
            else:
                self.question_label.setText(card_data["english"])
                self.current_question_is_japanese = False

        level = card_data["level"]
        color = self.LEVEL_COLORS.get(level, "#FFFFFF")
        self.card_frame.setStyleSheet(f"border: 3px solid {color};")

    def check_answer(self):
        card_data = self.deck[self.current_card_index]
        user_answer_romaji = self.answer_input.text().strip()

        self.kana_preview_label.hide()

        if self.current_question_is_japanese:
            correct_answer = card_data["english"]
            is_correct = user_answer_romaji.lower().strip() == correct_answer.lower().strip()
            feedback_answer = correct_answer
        else:
            if user_answer_romaji.isupper():
                user_answer_kana = romkan.to_katakana(user_answer_romaji)
            else:
                user_answer_kana = romkan.to_hiragana(user_answer_romaji)
            
            correct_answer_japanese = card_data["japanese"]
            correct_answer_reading = card_data["reading"]
            is_correct = user_answer_kana == correct_answer_japanese or (correct_answer_reading and user_answer_kana == correct_answer_reading)
            feedback_answer = f'{correct_answer_japanese} ({correct_answer_reading})'

        if is_correct:
            self.feedback_label.setText(f"Correct! The answer is {feedback_answer}")
            card_data["level"] = min(card_data["level"] + 1, 3)
        else:
            self.feedback_label.setText(f"Incorrect. Your answer: {user_answer_romaji}. Correct answer: {feedback_answer}")
            card_data["level"] = max(card_data["level"] - 1, 0)
        
        self.answer_input.hide()
        self.submit_button.hide()
        self.submit_button.setDefault(False)
        self.continue_button.show()
        self.continue_button.setDefault(True)
        self.continue_button.setFocus()

    def update_card(self):
        card_data = self.deck[self.current_card_index]
        card = card_data["card"]
        level = card_data["level"]
        options = card.options()
        
        if 0 <= level < len(options):
            new_card_state = options[level][1]
            self.deck[self.current_card_index]["card"] = new_card_state
        
        self.current_card_index += 1
        self.next_card()

    def _get_progress_path(self):
        if not self.deck_path:
            return None
        deck_name = os.path.splitext(os.path.basename(self.deck_path))[0]
        return os.path.join(os.path.dirname(__file__), '..', '..', 'progress_files', f"{deck_name}.json")

    def _load_progress(self):
        progress_path = self._get_progress_path()
        if progress_path and os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                progress_list = json.load(f)
                return {item['japanese']: item for item in progress_list}
        return {}

    def save_progress(self):
        progress_path = self._get_progress_path()
        if not progress_path:
            return

        progress_data = []
        default_card = Card()
        for card_data in self.deck:
            card = card_data["card"]
            is_default = (
                card.status == default_card.status and
                card_data["level"] == 0
            )
            if not is_default:
                progress_data.append({
                    "japanese": card_data["japanese"],
                    "reading": card_data["reading"],
                    "english": card_data["english"],
                    "card": card.to_dict(),
                    "level": card_data["level"]
                })

        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=4)