
import os
import json
import time
from unittest.mock import MagicMock, mock_open, patch
from frontend.widgets.progress import ProgressWidget
from PyQt6.QtWidgets import QLineEdit, QPushButton
from PyQt6.QtCore import Qt


def test_progress_widget(qtbot, monkeypatch):
    back_callback = MagicMock()

    # Mock file system
    progress_data = '[{"japanese": "勉強", "reading": "べんきょう", "english": "to study", "card": {"status": "reviewing", "step": 1, "interval": 86400.0, "ease": 2.5, "level": 2}, "last_reviewed_time": 1234567890}]'
    deck_data = '勉強,べんきょう,to study'
    
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

    # Mock time
    monkeypatch.setattr(time, "time", lambda: 1234567890 + 86400)

    widget = ProgressWidget(back_callback)
    qtbot.addWidget(widget)
    widget.show()

    # Load a deck
    deck_path = "/path/to/deck.csv"
    widget.load_deck(deck_path)

    # Check if the card is displayed
    assert len(widget.all_word_widgets) == 1
    assert widget.all_word_widgets[0].word_data.japanese == "勉強"

    # Check stats
    assert "Total Cards: 1" in widget.stats_label.text()
    assert "Cards Due: 1" in widget.stats_label.text()

    # Filter cards
    widget.search_input.setText("study")
    assert widget.all_word_widgets[0].isVisible()

    widget.search_input.setText("dog")
    assert not widget.all_word_widgets[0].isVisible()

    # Go back
    qtbot.mouseClick(widget.findChild(QPushButton, "back_button"), Qt.MouseButton.LeftButton)
    back_callback.assert_called_once()
