import os
from unittest.mock import MagicMock
from frontend.widgets.study_menu import StudyMenuWidget
from PyQt6.QtWidgets import QPushButton, QRadioButton
from PyQt6.QtCore import Qt

def test_study_menu_widget(qtbot, monkeypatch):
    back_callback = MagicMock()
    study_deck_callback = MagicMock()

    # Mock os.listdir to return a predictable list of files
    monkeypatch.setattr(os, "listdir", lambda path: ["N5.csv", "N4.csv"])

    widget = StudyMenuWidget(back_callback, study_deck_callback)
    qtbot.addWidget(widget)

    # Check if the buttons are there
    assert widget.findChild(QPushButton, "deck_button_N5")
    assert widget.findChild(QPushButton, "deck_button_N4")
    assert widget.findChild(QPushButton, "back_button")
    assert widget.findChild(QRadioButton, "eng_to_jap_radio")
    assert widget.findChild(QRadioButton, "jap_to_eng_radio")
    assert widget.findChild(QRadioButton, "mixed_radio")

    # Simulate button clicks
    qtbot.mouseClick(widget.findChild(QPushButton, "deck_button_N5"), Qt.MouseButton.LeftButton)
    expected_path = os.path.join(widget.vocab_path, "N5.csv")
    study_deck_callback.assert_called_once_with(expected_path, "eng_to_jap")

    # Change mode and test again
    widget.findChild(QRadioButton, "jap_to_eng_radio").setChecked(True)
    qtbot.mouseClick(widget.findChild(QPushButton, "deck_button_N4"), Qt.MouseButton.LeftButton)
    expected_path = os.path.join(widget.vocab_path, "N4.csv")
    study_deck_callback.assert_called_with(expected_path, "jap_to_eng")

    qtbot.mouseClick(widget.findChild(QPushButton, "back_button"), Qt.MouseButton.LeftButton)
    back_callback.assert_called_once()