import os
import json
import time
from unittest.mock import MagicMock, patch, mock_open
from frontend.widgets.study_session import StudySessionWidget
from PyQt6.QtWidgets import QPushButton, QLineEdit
from PyQt6.QtCore import Qt


def test_study_session_widget(qtbot, monkeypatch):
    back_callback = MagicMock()

    # Mock file system
    progress_data = '[{"japanese": "勉強", "reading": "べんきょう", "english": "to study", "card": {"status": "learning", "step": 0, "interval": 0.0, "ease": 2.5, "level": 0}, "last_reviewed_time": 1234567890}]'
    deck_data = '''勉強,べんきょう,to study
犬,いぬ,dog'''
    
    file_mocks = {
        "/mnt/d/projects/benkyou/progress_files/deck.json": mock_open(read_data=progress_data).return_value,
        "/path/to/deck.csv": mock_open(read_data=deck_data).return_value
    }

    def mock_open_logic(path, *args, **kwargs):
        if path in file_mocks:
            return file_mocks[path]
        # Fallback for other files if needed, or raise an error for unexpected opens
        return mock_open()(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_logic)
    monkeypatch.setattr(os.path, "exists", lambda path: path in file_mocks)

    # Mock time
    monkeypatch.setattr(time, "time", lambda: 1234567890)

    widget = StudySessionWidget(back_callback)
    qtbot.addWidget(widget)

    # Start a study session
    deck_path = "/path/to/deck.csv"
    mode = "eng_to_jap"
    widget.start_study_session(deck_path, mode)

    # Check if the first card is displayed
    assert widget.question_label.text() == "to study"

    # Simulate typing the correct answer
    widget.answer_input.setText("benkyou")
    qtbot.keyClick(widget.answer_input, Qt.Key.Key_Return)

    # Check feedback
    assert "Correct!" in widget.feedback_label.text()

    # Continue to the next card
    qtbot.mouseClick(widget.continue_button, Qt.MouseButton.LeftButton)

    # Check if the second card is displayed
    assert widget.question_label.text() == "dog"

    # Simulate typing the wrong answer
    widget.answer_input.setText("wrong")
    qtbot.keyClick(widget.answer_input, Qt.Key.Key_Return)

    # Check feedback
    assert "Incorrect." in widget.feedback_label.text()

    # Save progress
    widget.save_progress()

    # Go back
    qtbot.mouseClick(widget.back_button, Qt.MouseButton.LeftButton)
    back_callback.assert_called_once()


def test_reward_user_function(qtbot, monkeypatch):
    """Test that reward_user function is called when answer is correct."""
    back_callback = MagicMock()

    # Mock file system
    progress_data = '[{"japanese": "勉強", "reading": "べんきょう", "english": "to study", "card": {"status": "learning", "step": 0, "interval": 0.0, "ease": 2.5, "level": 0}, "last_reviewed_time": 1234567890}]'
    deck_data = '''勉強,べんきょう,to study'''
    
    file_mocks = {
        "/mnt/d/projects/benkyou/progress_files/deck.json": mock_open(read_data=progress_data).return_value,
        "/path/to/deck.csv": mock_open(read_data=deck_data).return_value
    }

    def mock_open_logic(path, *args, **kwargs):
        if path in file_mocks:
            return file_mocks[path]
        return mock_open()(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_logic)
    monkeypatch.setattr(os.path, "exists", lambda path: path in file_mocks)
    monkeypatch.setattr(time, "time", lambda: 1234567890)

    widget = StudySessionWidget(back_callback)
    qtbot.addWidget(widget)

    # Mock the reward_user function to verify it's called
    with patch.object(widget, 'reward_user') as mock_reward:
        # Start a study session
        deck_path = "/path/to/deck.csv"
        mode = "eng_to_jap"
        widget.start_study_session(deck_path, mode)

        # Simulate typing the correct answer
        widget.answer_input.setText("benkyou")
        qtbot.keyClick(widget.answer_input, Qt.Key.Key_Return)

        # Verify reward_user was called
        mock_reward.assert_called_once()


def test_reward_animation_properties(qtbot):
    """Test that reward animation properties are properly initialized."""
    back_callback = MagicMock()
    widget = StudySessionWidget(back_callback)
    qtbot.addWidget(widget)

    # Check that animation properties are initialized
    assert hasattr(widget, 'animation_timer')
    assert hasattr(widget, 'animation_phase')
    assert hasattr(widget, 'original_style')
    
    # Check initial values
    assert widget.animation_phase == 0
    assert widget.original_style == ""