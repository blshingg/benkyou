from unittest.mock import MagicMock
from frontend.widgets.main_menu import MainMenuWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

def test_main_menu_widget(qtbot):
    study_callback = MagicMock()
    show_progress_menu_callback = MagicMock()
    quit_callback = MagicMock()

    widget = MainMenuWidget(study_callback, show_progress_menu_callback, quit_callback)
    qtbot.addWidget(widget)

    # Check if the buttons are there
    assert widget.findChild(QPushButton, "study_button")
    assert widget.findChild(QPushButton, "progress_button")
    assert widget.findChild(QPushButton, "quit_button")

    # Simulate button clicks
    qtbot.mouseClick(widget.findChild(QPushButton, "study_button"), Qt.MouseButton.LeftButton)
    study_callback.assert_called_once()

    qtbot.mouseClick(widget.findChild(QPushButton, "progress_button"), Qt.MouseButton.LeftButton)
    show_progress_menu_callback.assert_called_once()

    qtbot.mouseClick(widget.findChild(QPushButton, "quit_button"), Qt.MouseButton.LeftButton)
    quit_callback.assert_called_once()