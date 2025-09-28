import csv
import os
import sys
import json
import random
import time
import threading
import platform
import numpy as np
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

if platform.system().lower() == "windows":
    import winsound

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from spaced_repetition.card import Card
from spaced_repetition.card_data import CardData
import translation.romaji_to_kana as romkan
from spaced_repetition.deck import Deck

class StudySessionWidget(QWidget):
    LEVEL_COLORS = {
        0: "#808080",  # Gray
        1: "#ADAD85",  # Yellow-Gray
        2: "#FFFF00",  # Yellow
        3: "#00FF00",  # Green
    }

    current_card: Card
    deck_manager: Deck
    deck_path: str
    mode: str
    current_question_is_japanese: bool
    previous_question_correct: int = 0 # 1 or -1 unless just initialized

    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self.deck_manager = Deck()
        self.current_card = None # Store the current card being studied
        self.deck_path = None
        self.mode = None
        self.current_question_is_japanese = False
        
        
        # Initialize animation properties
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_phase = 0
        self.original_style = ""

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
        self.back_button.clicked.connect(lambda: (self.save_progress(), self.back_callback()))
        layout.addWidget(self.back_button)

        self.answer_input.textChanged.connect(self.on_text_changed)

    def reward_user(self) -> None:
        """Play sound effect and show reward animation when user gets correct answer."""
        # Start the reward animation immediately
        self._start_reward_animation()
        
        # Play jingle in a separate thread so it doesn't block the animation
        threading.Thread(target=self._play_jingle, daemon=True).start()

    def _generate_tone(self, frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Generate a sine wave tone with the specified frequency and duration."""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        return np.sin(2 * np.pi * frequency * t)

    def _play_jingle(self) -> None:
        """Play a pleasant jingle using platform-specific sound function."""
        try:
            system = platform.system().lower()
            if system == "windows":
                self._play_jingle_windows()
            elif system == "linux":
                self._play_jingle_linux()
            elif system == "darwin":  # macOS
                self._play_jingle_mac()
            else:
                # Fallback to Windows method for unknown systems
                self._play_jingle_windows()
        except:
            pass

    def _play_jingle_windows(self) -> None:
        """Play a pleasant jingle on Windows using winsound."""
        # Play a faster ascending jingle: C-E-G (do-mi-sol)
        # C4 = 261.63 Hz, E4 = 329.63 Hz, G4 = 392.00 Hz
        winsound.Beep(262, 150)  # C4 - faster
        winsound.Beep(330, 150)  # E4 - faster
        winsound.Beep(392, 150)  # G4 - slightly longer but still faster
        winsound.Beep(440, 150)  # A4 - slightly longer but still faster

    def _play_jingle_linux(self) -> None:
        """Play a pleasant jingle on Linux using sounddevice."""
        if not SOUNDDEVICE_AVAILABLE:
            return
        
        # Play a faster ascending jingle: C-E-G (do-mi-sol)
        # C4 = 261.63 Hz, E4 = 329.63 Hz, G4 = 392.00 Hz, A4 = 440.00 Hz
        frequencies = [262, 330, 392, 440]
        duration = 0.15  # 150ms
        
        for freq in frequencies:
            tone = self._generate_tone(freq, duration)
            sd.play(tone, samplerate=44100)
            sd.wait()  # Wait for the tone to finish playing

    def _play_jingle_mac(self) -> None:
        """Play a pleasant jingle on macOS using sounddevice."""
        if not SOUNDDEVICE_AVAILABLE:
            return
        
        # Play a faster ascending jingle: C-E-G (do-mi-sol)
        # C4 = 261.63 Hz, E4 = 329.63 Hz, G4 = 392.00 Hz, A4 = 440.00 Hz
        frequencies = [262, 330, 392, 440]
        duration = 0.15  # 150ms
        
        for freq in frequencies:
            tone = self._generate_tone(freq, duration)
            sd.play(tone, samplerate=44100)
            sd.wait()  # Wait for the tone to finish playing

    def _start_reward_animation(self) -> None:
        """Start a subtle pulsing/fireworks animation effect."""
        self.original_style = self.card_frame.styleSheet()
        self.animation_phase = 0
        self.animation_timer.start(50)  # Update every 50ms for smooth animation

    def _update_animation(self) -> None:
        """Update the reward animation frame."""
        self.animation_phase += 1
        
        if self.animation_phase > 20:  # Animation duration: 1 second (20 * 50ms)
            self.animation_timer.stop()
            self.card_frame.setStyleSheet(self.original_style)
            return
        
        # Create a pulsing effect with color changes
        progress = self.animation_phase / 20.0
        
        # Create a subtle pulsing effect with golden colors
        if progress < 0.5:
            # First half: pulse in with golden color
            intensity = progress * 2
            alpha = int(100 + intensity * 155)  # 100-255 alpha
            color = f"rgba(255, 215, 0, {alpha})"  # Gold color
        else:
            # Second half: pulse out with green color
            intensity = (1.0 - progress) * 2
            alpha = int(100 + intensity * 155)  # 100-255 alpha
            color = f"rgba(0, 255, 0, {alpha})"  # Green color
        
        # Apply the animated style
        animated_style = f"""
            border: 5px solid {color};
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        """
        self.card_frame.setStyleSheet(animated_style)

    def _convert_mixed_case_to_kana(self, text: str) -> str:
        """Convert text to kana with mixed case handling.
        """
        if not text:
            return ""
        
        
        # Find segment boundaries where case changes
        result = ""
        is_current_segment_upper = None
        current_start = 0
        
        for i, char in enumerate(text):
            char_case = char.isupper()
            if is_current_segment_upper is None:
                is_current_segment_upper = char_case
            elif char_case != is_current_segment_upper:
                # Case changed, save current segment
                if is_current_segment_upper:
                    result += romkan.to_katakana(text[current_start:i])
                else:
                    result += romkan.to_hiragana(text[current_start:i])
                current_start = i
                is_current_segment_upper = char_case

        if current_start < len(text) or len(result) < len(text):
            if is_current_segment_upper:
                result += romkan.to_katakana(text[current_start:i + 1])
            else:
                result += romkan.to_hiragana(text[current_start:i + 1])
        
        return result

    def on_text_changed(self, text):
        if not self.current_question_is_japanese:
            kana = self._convert_mixed_case_to_kana(text)
            self.kana_preview_label.setText(kana)
        else:
            self.kana_preview_label.setText("")

    def start_study_session(self, deck_path, mode):
        self.deck_manager = Deck()
        self.deck_path = deck_path
        self.mode = mode
        
        progress_data = self._load_progress()
        
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
                    
                    card_data = CardData(
                        card=card,
                        japanese=japanese,
                        english=english,
                        reading=reading,
                        level=level,
                        last_reviewed_time=last_reviewed
                    )
                    self.deck_manager.requeue_card(card_data)
        
        self.deck_manager.shuffle()
        self.next_card()

    def next_card(self):
        self.current_card = self.deck_manager.get_next_card()

        if self.current_card is None:
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

        card_data = self.current_card
        
        if self.mode == "eng_to_jap":
            self.question_label.setText(card_data.english)
            self.current_question_is_japanese = False
        elif self.mode == "jap_to_eng":
            self.question_label.setText(card_data.japanese)
            self.current_question_is_japanese = True
        else: # mixed mode
            if random.choice([True, False]):
                self.question_label.setText(card_data.japanese)
                self.current_question_is_japanese = True
            else:
                self.question_label.setText(card_data.english)
                self.current_question_is_japanese = False

        level = card_data.level
        color = self.LEVEL_COLORS.get(level, "#FFFFFF")
        self.card_frame.setStyleSheet(f"border: 3px solid {color};")

    def check_answer(self):
        card_data = self.current_card
        user_answer_romaji = self.answer_input.text().strip()

        self.kana_preview_label.hide()

        if self.current_question_is_japanese:
            correct_answer = card_data.english
            is_correct = user_answer_romaji.lower().strip() in correct_answer.lower().strip() and len(user_answer_romaji) != 0
            feedback_answer = correct_answer
        else:
            user_answer_kana = self._convert_mixed_case_to_kana(user_answer_romaji)
            correct_answer_japanese = card_data.japanese
            correct_answer_reading = card_data.reading
            is_correct = user_answer_kana == correct_answer_japanese or (correct_answer_reading and user_answer_kana == correct_answer_reading)
            feedback_answer = f'{correct_answer_japanese} ({correct_answer_reading})'

        if is_correct:
            self.feedback_label.setText(f"Correct! The answer is {feedback_answer}")
            card_data.level = min(card_data.level + 1, 3)
            self.previous_question_correct = 1
            self.reward_user()
        else:
            self.feedback_label.setText(f"Incorrect. Your answer: {self._convert_mixed_case_to_kana(user_answer_romaji)}. Correct answer: {feedback_answer}")
            card_data.level = max(card_data.level - 1, 0)
            self.previous_question_correct = -1
        
        card_data.last_reviewed_time = time.time()

        self.answer_input.hide()
        self.submit_button.hide()
        self.submit_button.setDefault(False)
        self.continue_button.show()
        self.continue_button.setDefault(True)
        self.continue_button.setFocus()

    def update_card(self):
        card_data = self.current_card
        card = card_data.card
        level = card_data.level
        options = card.options(self.previous_question_correct)
        
        if 0 <= level < len(options):
            new_card = options[level][1]
            card_data.card = new_card
        
        self.deck_manager.requeue_card(card_data)
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
        for card_data in [self.current_card] + self.deck_manager.get_all_cards():
            card = card_data.card.to_dict()
            is_default = (
                card["status"] == default_card.status and
                card["level"] == default_card.level
            )
            if not is_default:
                progress_data.append({
                    "japanese": card_data.japanese,
                    "reading": card_data.reading,
                    "english": card_data.english,
                    "card": card,
                    "last_reviewed_time": card_data.last_reviewed_time
                })
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=4)