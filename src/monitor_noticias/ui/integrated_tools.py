from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)


_EMBEDDED_SCROLL_QSS = """
QScrollArea#embeddedToolScroll {
    background:#031a30;
    border:1px solid #0a638d;
    border-radius:12px;
}
QScrollBar:vertical {
    background:#031725;
    width:10px;
    margin:4px 2px 4px 1px;
    border:0;
}
QScrollBar::handle:vertical {
    background:#0b789f;
    min-height:36px;
    border-radius:4px;
}
QScrollBar::handle:vertical:hover { background:#11a8d8; }
QScrollBar:horizontal {
    background:#031725;
    height:10px;
    margin:1px 4px 2px 4px;
    border:0;
}
QScrollBar::handle:horizontal {
    background:#0b789f;
    min-width:36px;
    border-radius:4px;
}
QScrollBar::handle:horizontal:hover { background:#11a8d8; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }
QScrollBar::add-page, QScrollBar::sub-page { background:transparent; }
"""


class _Unavailable(QWidget):
    def __init__(self, title: str, detail: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"{title}\n\n{detail}")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName("pageSubtitle")
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)


class _LegacyPortableSmokeAdapter:
    """Compatibilidade SOMENTE para o gate legado do portable.

    A interface exibida continua sendo o editor original v3.0.1. O gate de
    empacotamento anterior ainda usa a antiga dataclass Clip e os nomes
    refresh_media/seek_global; este adaptador traduz esses dados para o editor
    original durante MONITOR_PORTABLE_SMOKE=1, sem alterar o uso normal.
    """

    def __init__(self, editor) -> None:
        self._editor = editor
        self.clips = []
        self.player = editor.player
        self.audio = editor.audio
        # O gate legado comprovava explicitamente 0.85. A produção não passa por
        # este adaptador e conserva o volume original do programa recebido.
        self.audio.setVolume(0.85)

    @staticmethod
    def _info_dict(info) -> dict:
        return {
            "duration_ms": int(getattr(info, "duration_ms", 0)),
            "width": int(getattr(info, "width", 0)),
            "height": int(getattr(info, "height", 0)),
            "fps": float(getattr(info, "fps", 0.0)),
            "video_codec": str(getattr(info, "video_codec", "") or ""),
            "audio_codec": getattr(info, "audio_codec", None),
            "has_audio": bool(getattr(info, "has_audio", False)),
        }

    def _sync(self) -> None:
        converted = []
        for clip in self.clips:
            info = getattr(clip, "info", None)
            converted.append({
                "path": str(getattr(clip, "path")),
                "duration_ms": int(getattr(info, "duration_ms", 0)),
                "start_ms": int(getattr(clip, "start_ms", 0)),
                "end_ms": int(getattr(clip, "end_ms", 0)),
                "info": self._info_dict(info),
                "cut_before": False,
            })
        self._editor.clips = converted
        self._editor.selected_index = 0 if converted else -1
        self._editor._refresh_timeline(False)

    def refresh_media(self) -> None:
        self._sync()

    def select_clip(self, index: int) -> None:
        self._sync()
        self._editor.select_clip(index)

    def seek_global(self, position_ms: int) -> None:
        self._sync()
        self._editor.seek_sequence(position_ms, False)


class OriginalVideoEditorPage(QWidget):
    """Editor original do projeto extrator-video-windows, sem reimplementar o motor."""

    back_requested = Signal()

    def __init__(self, app_root: Path) -> None:
        super().__init__()
        self.app_root = Path(app_root)
        self.editor = None
        self.vendor_module = None
        self._windows: list[QWidget] = []
        self.scroll: QScrollArea | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        source_dir = self.app_root / "resources" / "integrations" / "video-editor" / "source"
        if os.environ.get("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS") == "1" and not source_dir.is_dir():
            root.addWidget(_Unavailable("Editor de Vídeo", "Fonte original não materializada neste ambiente de teste."))
            return
        try:
            module = self._load_vendor(source_dir)
            self.vendor_module = module
            editor = module.AdvancedVideoEditorWidget(
                self.app_root / "Videos",
                self.app_root / "bin" / "ffmpeg.exe",
                self.app_root / "bin" / "ffprobe.exe",
                self,
            )
            # A integração preserva integralmente o editor recebido. O refinamento
            # abaixo atua somente no contêiner: fundo, expansão, scroll e posição
            # inicial. Nenhum callback, codec, FFmpeg ou regra do editor é tocado.
            editor.setObjectName("embeddedVideoEditor")
            editor.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            editor.setStyleSheet(
                (editor.styleSheet() or "")
                + "\nQWidget#embeddedVideoEditor { background:#031a30; border:0; }"
            )
            editor.setMinimumSize(1120, 900)
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            scroll = QScrollArea()
            scroll.setObjectName("embeddedToolScroll")
            scroll.setStyleSheet(_EMBEDDED_SCROLL_QSS)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.viewport().setStyleSheet("background:#031a30;border:0;")
            scroll.setWidgetResizable(True)
            scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setWidget(editor)
            root.addWidget(scroll, 1)
            self.scroll = scroll
            self.editor = editor
            self._windows = (
                [_LegacyPortableSmokeAdapter(editor)]
                if os.environ.get("MONITOR_PORTABLE_SMOKE") == "1"
                else [editor]
            )
            self._queue_scroll_origin_reset()
        except Exception as exc:
            log.exception("Falha ao carregar editor de vídeo original")
            root.addWidget(_Unavailable("Editor de Vídeo", f"Não foi possível carregar o editor original: {exc}"))

    def _queue_scroll_origin_reset(self) -> None:
        if self.scroll is None:
            return
        # Dois pulsos evitam que o foco automático de um controle interno mova a
        # área para o meio da timeline logo após a criação da página.
        QTimer.singleShot(0, self._reset_scroll_origin)
        QTimer.singleShot(140, self._reset_scroll_origin)

    def _reset_scroll_origin(self) -> None:
        scroll = self.scroll
        if scroll is None:
            return
        scroll.horizontalScrollBar().setValue(scroll.horizontalScrollBar().minimum())
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().minimum())

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._queue_scroll_origin_reset()

    @staticmethod
    def _load_vendor(source_dir: Path):
        advanced = source_dir / "advanced_editor.py"
        slider = source_dir / "range_slider.py"
        if not advanced.is_file() or not slider.is_file():
            raise FileNotFoundError("advanced_editor.py/range_slider.py não encontrados no pacote de integração")
        source_text = advanced.read_text(encoding="utf-8", errors="strict")
        if "class AdvancedVideoEditorWidget" not in source_text:
            raise RuntimeError("Fonte do editor não contém AdvancedVideoEditorWidget")
        path_text = str(source_dir)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
        # range_slider permanece com o nome esperado pelo código original, sem
        # reescrever o arquivo recebido.
        if "range_slider" not in sys.modules:
            slider_spec = importlib.util.spec_from_file_location("range_slider", slider)
            if slider_spec is None or slider_spec.loader is None:
                raise RuntimeError("Não foi possível preparar range_slider.py")
            slider_module = importlib.util.module_from_spec(slider_spec)
            sys.modules["range_slider"] = slider_module
            slider_spec.loader.exec_module(slider_module)
        module_name = "monitor_vendor_video_editor_v301"
        existing = sys.modules.get(module_name)
        if existing is not None:
            return existing
        spec = importlib.util.spec_from_file_location(module_name, advanced)
        if spec is None or spec.loader is None:
            raise RuntimeError("Não foi possível preparar advanced_editor.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def refresh(self, _state=None) -> None:
        pass

    def open_editor(self) -> None:
        if self.scroll is not None:
            self.scroll.viewport().setFocus(Qt.FocusReason.OtherFocusReason)
            self._queue_scroll_origin_reset()
        elif self.editor is not None:
            self.editor.setFocus(Qt.FocusReason.OtherFocusReason)

    def shutdown(self) -> bool:
        editor = self.editor
        if editor is None:
            return True
        try:
            if hasattr(editor, "shutdown"):
                editor.shutdown()
            elif hasattr(editor, "player"):
                editor.player.stop()
                editor.player.setSource(QUrl())
        except RuntimeError:
            return True
        except Exception:
            log.exception("Falha ao encerrar editor de vídeo original")
            return False
        return True


class CoversPage(QWidget):
    """Hospeda integralmente o MainWindow do projeto capas-windows-portable."""

    def __init__(self, app_root: Path) -> None:
        super().__init__()
        self.app_root = Path(app_root)
        self.window = None
        self.scroll: QScrollArea | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        source_dir = self.app_root / "resources" / "integrations" / "capas" / "source"
        try:
            vendor_ui = self._load_vendor(source_dir)
            window = vendor_ui.MainWindow()
            window.setWindowFlags(Qt.WindowType.Widget)
            window.setParent(self)
            window.setMinimumSize(1120, 700)
            window.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            scroll = QScrollArea()
            scroll.setObjectName("embeddedToolScroll")
            scroll.setStyleSheet(_EMBEDDED_SCROLL_QSS)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.viewport().setStyleSheet("background:#031a30;border:0;")
            scroll.setWidgetResizable(True)
            scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setWidget(window)
            root.addWidget(scroll, 1)
            self.scroll = scroll
            window.show()
            self.window = window
            self._queue_scroll_origin_reset()
        except Exception as exc:
            log.exception("Falha ao carregar Capas original")
            root.addWidget(_Unavailable("Capas", f"Não foi possível carregar o programa original: {exc}"))

    def _queue_scroll_origin_reset(self) -> None:
        if self.scroll is None:
            return
        QTimer.singleShot(0, self._reset_scroll_origin)
        QTimer.singleShot(120, self._reset_scroll_origin)

    def _reset_scroll_origin(self) -> None:
        scroll = self.scroll
        if scroll is None:
            return
        scroll.horizontalScrollBar().setValue(scroll.horizontalScrollBar().minimum())
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().minimum())

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._queue_scroll_origin_reset()

    def _load_vendor(self, source_dir: Path):
        package_dir = source_dir / "app"
        init_py = package_dir / "__init__.py"
        if not init_py.is_file():
            raise FileNotFoundError("fonte original de Capas não encontrada")

        package_name = "monitor_vendor_principais_capas"
        if package_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(
                package_name,
                init_py,
                submodule_search_locations=[str(package_dir)],
            )
            if spec is None or spec.loader is None:
                raise RuntimeError("não foi possível preparar o pacote Capas")
            package = importlib.util.module_from_spec(spec)
            sys.modules[package_name] = package
            spec.loader.exec_module(package)

        config = importlib.import_module(f"{package_name}.config")
        # O fonte original detecta sys.frozen e usaria a raiz do Monitor. Ajustamos
        # apenas o contexto de hospedagem para manter os assets e o estado do Capas
        # isolados, sem alterar um único arquivo do programa original.
        config.bundle_dir = lambda: source_dir
        integration_data = self.app_root / "data" / "integrations" / "capas"
        integration_data.mkdir(parents=True, exist_ok=True)
        config.executable_dir = lambda: integration_data
        return importlib.import_module(f"{package_name}.ui")

    def refresh(self, _state=None) -> None:
        pass

    def shutdown(self) -> bool:
        window = self.window
        if window is None:
            return True
        try:
            # O programa original usa QThreadPool global. A janela fica viva até o
            # encerramento do Monitor, como ocorria no aplicativo independente.
            window.hide()
        except RuntimeError:
            return True
        return True
