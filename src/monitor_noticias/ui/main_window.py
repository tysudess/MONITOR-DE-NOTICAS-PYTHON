from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Monitor de Notícias — Fundação Python")
        self.resize(820, 460)

        central = QWidget(self)
        layout = QVBoxLayout(central)
        label = QLabel(
            "Fundação técnica da migração Python\n"
            "Funcionalidades de negócio ainda não migradas."
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setCentralWidget(central)
