import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from frontend.widgets.main_menu import MainMenuWidget
from frontend.widgets.study_menu import StudyMenuWidget
from frontend.widgets.progress import ProgressWidget
from frontend.widgets.study_session import StudySessionWidget
from frontend.widgets.progress_menu import ProgressMenuWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Benkyou")
        self.resize(800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_menu = MainMenuWidget(self.show_study_menu, self.show_progress_menu, self.close)
        self.study_menu = StudyMenuWidget(self.show_main_menu, self.show_study_session)
        self.progress_menu = ProgressMenuWidget(self.show_main_menu, self.show_progress_for_deck)
        self.progress_screen = ProgressWidget(self.show_main_menu)
        self.study_session = StudySessionWidget(self.show_study_menu)

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.study_menu)
        self.stacked_widget.addWidget(self.progress_menu)
        self.stacked_widget.addWidget(self.progress_screen)
        self.stacked_widget.addWidget(self.study_session)

        self.show_main_menu()

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def show_study_menu(self):
        self.stacked_widget.setCurrentWidget(self.study_menu)

    def show_progress_menu(self):
        self.stacked_widget.setCurrentWidget(self.progress_menu)

    def show_progress_for_deck(self, deck_path):
        self.stacked_widget.setCurrentWidget(self.progress_screen)
        self.progress_screen.load_deck(deck_path)

    def show_study_session(self, deck_path, mode):
        self.study_session.start_study_session(deck_path, mode)
        self.stacked_widget.setCurrentWidget(self.study_session)


    def closeEvent(self, event):
        if self.study_session.deck_manager is not None:
            self.study_session.save_progress()
        event.accept()

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())