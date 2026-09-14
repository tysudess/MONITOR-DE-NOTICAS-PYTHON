from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from monitor_noticias.video_editor.window import VideoEditorWindow


class VideoEditorPage(QWidget):
    """Hospeda o editor PySide6 dentro do QStackedWidget principal do Monitor.

    O motor do VideoEditorWindow (QMediaPlayer, QVideoWidget, timeline e FFmpeg)
    permanece intacto. A mudança é somente de hospedagem visual: o QMainWindow do
    editor vira um widget filho da página, portanto não abre outra janela.
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
            "Preview, áudio, timeline e exportação permanecem no mesmo motor; agora tudo funciona dentro do Monitor."
        )
        subtitle.setObjectName("smallText")
        subtitle.setWordWrap(True)
        titles.addWidget(title)
        titles.addWidget(subtitle)
        tl.addLayout(titles, 1)
        integrated = QLabel("●  Integrado")
        integrated.setStyleSheet(
            "color:#19e5a1;border:1px solid #0ba779;background:#063b3f;"
            "border-radius:7px;padding:6px 10px;font-weight:700;"
        )
        tl.addWidget(integrated)
        back = QPushButton("←  Voltar ao Monitor")
        back.setProperty("secondary", True)
        back.clicked.connect(self.back_requested.emit)
        tl.addWidget(back)
        root.addWidget(toolbar)

        self.editor = VideoEditorWindow(self.app_root)
        # Um QMainWindow também é QWidget. Transformá-lo em Qt.Widget preserva
        # centralWidget, QStatusBar, player, sinais e diálogos, mas remove o papel
        # de janela top-level que causava a abertura fora do Monitor.
        self.editor.setWindowFlags(Qt.WindowType.Widget)
        self.editor.setParent(self)
        self.editor.setMinimumSize(0, 0)

        # Compatibilidade com o gate portable legado: historicamente o launcher
        # expunha uma lista de janelas. Agora há um único editor incorporado, mas
        # mantemos a mesma referência para o smoke exercitar exatamente o mesmo
        # motor sem reabrir uma janela top-level.
        self._windows = [self.editor]

        # A barra lateral interna do editor duplicava a navegação principal do
        # Monitor e comprimía preview/timeline. Ela é somente apresentação; as
        # funções continuam disponíveis nos controles reais do editor.
        for frame in self.editor.findChildren(QFrame):
            if frame.minimumWidth() == 210 and frame.maximumWidth() == 210:
                frame.hide()

        root.addWidget(self.editor, 1)
        self.editor.show()

    def refresh(self, _state=None) -> None:
        # O editor permanece vivo entre trocas de aba e conserva mídia/timeline.
        pass

    def open_editor(self) -> None:
        """Compatibilidade com chamadas antigas: apenas foca o editor incorporado."""
        self.editor.setFocus(Qt.FocusReason.OtherFocusReason)

    def shutdown(self) -> bool:
        """Encerra os handles do player sem criar/fechar janelas auxiliares."""
        try:
            self.editor.player.stop()
            self.editor.player.setSource(QUrl())
        except RuntimeError:
            return True
        return True
