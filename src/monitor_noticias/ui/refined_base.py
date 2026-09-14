from __future__ import annotations

from datetime import datetime
from urllib.parse import quote

from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget

from monitor_noticias.ui.controller import MainUiController, UiState


def secondary(button: QPushButton) -> QPushButton:
    button.setProperty("secondary", True)
    return button


def dangerous(button: QPushButton) -> QPushButton:
    button.setProperty("danger", True)
    return button


def card(name: str = "techCard", margins=(16, 12, 16, 12), spacing: int = 8) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


def heading(title: str, subtitle: str = "") -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 2)
    layout.setSpacing(1)
    label = QLabel(title)
    label.setObjectName("sectionTitle")
    layout.addWidget(label)
    if subtitle:
        sub = QLabel(subtitle)
        sub.setObjectName("smallText")
        sub.setWordWrap(True)
        layout.addWidget(sub)
    return widget


def format_time(ms: int) -> str:
    if not ms:
        return "—"
    return datetime.fromtimestamp(ms / 1000).strftime("%d/%m/%Y %H:%M")


def duration(ms: int) -> str:
    sec = max(0, int(ms // 1000))
    if sec < 60:
        return f"00:{sec:02d}"
    return f"{sec // 60:02d}:{sec % 60:02d}"


def open_url(url: str) -> None:
    if url:
        QDesktopServices.openUrl(QUrl(url))


def copy_text(text: str) -> None:
    QApplication.clipboard().setText(text)


def open_whatsapp(title: str, url: str) -> None:
    open_url("https://wa.me/?text=" + quote(f"{title}\n{url}"))


class BasePage(QWidget):
    def __init__(self, controller: MainUiController) -> None:
        super().__init__()
        self.controller = controller
        self.setObjectName("pageRoot")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(12)

    def refresh(self, state: UiState) -> None:
        pass


class ToggleSwitch(QPushButton):
    def __init__(self, checked: bool = False) -> None:
        super().__init__("●")
        self.setCheckable(True)
        self.setFixedSize(58, 30)
        self.setChecked(checked)
        self.toggled.connect(self._sync)
        self._sync(checked)

    def _sync(self, checked: bool) -> None:
        pad = "padding-left:29px;" if checked else "padding-right:29px;"
        bg = "#087af7" if checked else "#40566d"
        border = "#25c9ff" if checked else "#93a9bd"
        self.setStyleSheet(
            f"QPushButton{{background:{bg};color:white;border:1px solid {border};border-radius:15px;"
            f"font-size:19px;min-height:28px;max-height:28px;{pad}}}"
            "QPushButton:hover{border-color:#79ddff;}"
        )


class ProxyTestThread(QThread):
    completed = Signal(bool, str)

    def __init__(self, controller: MainUiController) -> None:
        super().__init__()
        self.controller = controller

    def run(self) -> None:
        try:
            ok, text = self.controller.test_proxy()
        except Exception as exc:
            ok, text = False, f"Falha no proxy: {str(exc) or exc.__class__.__name__}"
        self.completed.emit(ok, text)


class ExecutionPanel(QFrame):
    def __init__(self, kind: str) -> None:
        super().__init__()
        self.kind = kind
        self.setObjectName("techCard")
        box = QVBoxLayout(self)
        box.setContentsMargins(16, 12, 16, 12)
        box.setSpacing(7)
        top = QHBoxLayout()
        status_icon = QLabel("✓")
        status_icon.setFixedSize(42, 42)
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_icon.setStyleSheet("color:#0ff0a1;background:#074f48;border:1px solid #0a9f7c;border-radius:21px;font-size:23px;font-weight:800;")
        top.addWidget(status_icon)
        titles = QVBoxLayout()
        titles.setSpacing(0)
        self.title = QLabel()
        self.title.setObjectName("sectionTitle")
        self.status = QLabel()
        self.status.setObjectName("smallText")
        titles.addWidget(self.title)
        titles.addWidget(self.status)
        top.addLayout(titles, 1)
        self.metric_labels: dict[str, QLabel] = {}
        for key, caption in (("pct", "conclusão"), ("found", "encontrados"), ("fresh", "novos"), ("errors", "falhas"), ("steps", "etapas"), ("time", "tempo")):
            col = QVBoxLayout()
            col.setSpacing(0)
            value = QLabel("0")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setStyleSheet("color:#1caaff;font-size:15px;font-weight:800;")
            cap = QLabel(caption)
            cap.setObjectName("smallText")
            cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(value)
            col.addWidget(cap)
            top.addLayout(col)
            self.metric_labels[key] = value
        box.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        box.addWidget(self.progress)
        self.detail = QLabel()
        self.detail.setObjectName("greenText")
        self.detail.setStyleSheet("color:#18dca0;background:#073d45;border:1px solid #0a8b74;border-radius:7px;padding:7px 10px;")
        box.addWidget(self.detail)

    def set_state(self, busy: bool, progress, status: str, fresh: int, elapsed: int) -> None:
        fraction = max(0.0, min(1.0, float(getattr(progress, "fraction", 0.0)))) if busy else 1.0
        pct = round(fraction * 100)
        completed = getattr(progress, "completed", 0)
        total = getattr(progress, "total", 0)
        found = getattr(progress, "found", 0)
        errors = getattr(progress, "errors", 0)
        self.title.setText(f"{self.kind} • {'busca em andamento' if busy else 'última execução concluída'}")
        self.status.setText(status or ("Buscando..." if busy else "Pronto"))
        self.progress.setValue(pct)
        self.metric_labels["pct"].setText(f"{pct}%")
        self.metric_labels["found"].setText(str(found))
        self.metric_labels["fresh"].setText(str(fresh))
        self.metric_labels["errors"].setText(str(errors))
        self.metric_labels["steps"].setText(f"{completed}/{total}")
        self.metric_labels["time"].setText(duration(elapsed))
        if busy:
            source = getattr(progress, "currentSource", "") or "Preparando..."
            query = getattr(progress, "currentQuery", "") or "Preparando consulta..."
            self.detail.setText(f"{source} • {query}")
        else:
            self.detail.setText(f"{fresh} novo(s) nesta execução. A marcação Nova é recalculada a cada nova busca.")
