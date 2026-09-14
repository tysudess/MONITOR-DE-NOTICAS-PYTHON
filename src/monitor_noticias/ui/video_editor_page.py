from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from monitor_noticias.video_editor.window import VideoEditorWindow


class VideoEditorPage(QWidget):
    """Hospeda o editor PySide6 dentro do QStackedWidget principal do Monitor.

    O motor do VideoEditorWindow (QMediaPlayer, QVideoWidget, timeline e FFmpeg)
    permanece o mesmo. A única mudança é de hospedagem: a centralWidget do editor
    é incorporada nesta página em vez de abrir uma janela top-level separada.
    """

    back_requested = Signal()

    def __init__(self, app_root: Path) -> None:
        super().__init__()
        self.app_root = Path(app_root)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        toolbar = QFrame()
        toolbar.setObjectName("filterCard")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(14, 8, 14, 8)
        titles = QVBoxLayout()
        titles.setSpacing(1)
        title = QLabel("Editor de Vídeo integrado")
        title.setObjectName("sectionTitle")
        subtitle = QLabel(
            "Preview, áudio, timeline e exportação permanecem no mesmo motor; agora tudo abre dentro do Monitor."
        )
        subtitle.setObjectName("smallText")
        subtitle.setWordWrap(True)
        titles.addWidget(title)
        titles.addWidget(subtitle)
        tl.addLayout(titles, 1)
        back = QPushButton("←  Voltar ao Monitor")
        back.setProperty("secondary", True)
        back.clicked.connect(self.back_requested.emit)
        tl.addWidget(back)
        root.addWidget(toolbar)

        self.editor = VideoEditorWindow(self.app_root)
        self.editor.hide()
        self.workspace = self.editor.takeCentralWidget()
        if self.workspace is None:
            raise RuntimeError("O Editor de Vídeo não forneceu uma área central para integração.")
        self.workspace.setParent(self)
        # O tema original do editor era herdado do QMainWindow top-level. Ao
        # incorporar a centralWidget, reaplicamos a mesma folha visual nela.
        self.workspace.setStyleSheet(self.editor.styleSheet())
        root.addWidget(self.workspace, 1)

        status_card = QFrame()
        status_card.setObjectName("footerFrame")
        sl = QHBoxLayout(status_card)
        sl.setContentsMargins(10, 5, 10, 5)
        self.status = QLabel("Pronto. Abra um ou mais vídeos.")
        self.status.setObjectName("smallText")
        sl.addWidget(self.status, 1)
        integrated = QLabel("●  Editor integrado ao Monitor")
        integrated.setStyleSheet("color:#19e5a1;font-size:10px;font-weight:700;")
        sl.addWidget(integrated)
        root.addWidget(status_card)

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(250)
        self._status_timer.timeout.connect(self._sync_status)
        self._status_timer.start()
        self._sync_status()

    def _sync_status(self) -> None:
        try:
            message = self.editor.statusBar().currentMessage().strip()
        except RuntimeError:
            message = ""
        if message:
            self.status.setText(message)

    def refresh(self, _state=None) -> None:
        # A página já está viva dentro do Monitor; não abra nova janela ao navegar.
        self._sync_status()

    def open_editor(self) -> None:
        """Compatibilidade com chamadas antigas: apenas foca o editor incorporado."""
        self.workspace.setFocus(Qt.FocusReason.OtherFocusReason)
        self._sync_status()

    def shutdown(self) -> bool:
        """Encerra os handles do player sem criar/fechar janelas auxiliares."""
        self._status_timer.stop()
        try:
            self.editor.player.stop()
            self.editor.player.setSource(QUrl())
        except RuntimeError:
            return True
        return True
