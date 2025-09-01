import os
from unittest.mock import MagicMock
from frontend.widgets.progress_menu import ProgressMenuWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

def test_progress_menu_widget(qtbot, monkeypatch):
    back_callback = MagicMock()
    show_progress_for_deck_callback = MagicMock()

    # Mock os.listdir to return a predictable list of files
    monkeypatch.setattr(os, "listdir", lambda path: ["N5.csv", "N4.csv"])

    widget = ProgressMenuWidget(back_callback, show_progress_for_deck_callback)
    qtbot.addWidget(widget)

    # Check if the buttons are there
    assert widget.findChild(QPushButton, "deck_button_N5")
    assert widget.findChild(QPushButton, "deck_button_N4")
    assert widget.findChild(QPushButton, "back_button")

    # Simulate button clicks
    qtbot.mouseClick(widget.findChild(QPushButton, "deck_button_N5"), Qt.MouseButton.LeftButton)
    expected_path = os.path.join(widget.vocab_path, "N5.csv")
    show_progress_for_deck_callback.assert_called_once_with(expected_path)

    qtbot.mouseClick(widget.findChild(QPushButton, "back_button"), Qt.MouseButton.LeftButton)
    back_callback.assert_called_once()