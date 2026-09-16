from __future__ import annotations

"""v0.0.19 — reprodução literal da imagem-verdade na Home/shell.

Esta camada não troca controller, banco, coletores, páginas nem motores. A imagem
fornecida pelo usuário é a composição visual. Os controles reais continuam vivos
por cima dela como áreas transparentes de interação.
"""

import base64
import hashlib
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QScrollArea, QWidget

_INSTALLED = False
_REFERENCE: QPixmap | None = None
REFERENCE_SHA256 = "d36b34896671cfe632da2585e9cbb37e16999a9d417b5d8e77ebf961917f0d2f"
REFERENCE_BYTES = 54218
REFERENCE_WIDTH = 1672
REFERENCE_HEIGHT = 941
SIDEBAR_WIDTH = 225
TOPBAR_HEIGHT = 86


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "resources"
    return Path(__file__).resolve().parents[3] / "resources"


def _reference_pixmap() -> QPixmap:
    global _REFERENCE
    if _REFERENCE is not None and not _REFERENCE.isNull():
        return _REFERENCE
    folder = _resource_root() / "ui" / "v019" / "home-full-q20"
    parts = sorted(folder.glob("part*.b64"), key=lambda p: p.name)
    if not parts:
        raise RuntimeError("Imagem-verdade integral v0.0.19 ausente")
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    raw = base64.b64decode(encoded)
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) != REFERENCE_BYTES or digest != REFERENCE_SHA256:
        raise RuntimeError(f"Imagem-verdade integral divergente: bytes={len(raw)} sha256={digest}")
    pix = QPixmap()
    if not pix.loadFromData(raw, "WEBP"):
        raise RuntimeError("Imagem-verdade integral v0.0.19 não pôde ser decodificada")
    if pix.width() != REFERENCE_WIDTH or pix.height() != REFERENCE_HEIGHT:
        raise RuntimeError(f"Imagem-verdade com dimensão divergente: {pix.width()}x{pix.height()}")
    _REFERENCE = pix
    return pix


class _BackdropResizeFilter(QObject):
    def __init__(self, parent: QWidget, label: QLabel) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.label = label

    def eventFilter(self, obj, event):
        if obj is self.parent_widget and event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self.label.setGeometry(self.parent_widget.rect())
        return False


def _backdrop(parent: QWidget, name: str, source: QRect) -> QLabel:
    existing = parent.findChild(QLabel, name)
    if existing is None:
        existing = QLabel(parent)
        existing.setObjectName(name)
        existing.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        existing.setScaledContents(True)
        existing.setStyleSheet("background:transparent;border:0;")
        filt = _BackdropResizeFilter(parent, existing)
        parent.installEventFilter(filt)
        setattr(parent, f"_{name}_resize_filter", filt)
    existing.setPixmap(_reference_pixmap().copy(source))
    existing.setGeometry(parent.rect())
    existing.show()
    existing.lower()
    return existing


def _transparent_primary_nav(window) -> None:
    from monitor_noticias.ui.sections import Section

    primary = {
        Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
        Section.SOURCES, Section.HISTORY, Section.TERMS, Section.COVERS,
        Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
    }
    transparent = (
        "QPushButton{background:transparent;color:transparent;border:0;border-radius:0;"
        "padding:0;} QPushButton:hover,QPushButton:checked,QPushButton:pressed{"
        "background:transparent;color:transparent;border:0;}"
    )
    extra_style = (
        "QPushButton{background:#041d33;color:#eef7ff;border:1px solid #0b5d84;"
        "border-radius:9px;padding:9px 11px;text-align:left;font-size:12px;font-weight:600;}"
        "QPushButton:hover{background:#06304f;border-color:#00c9ff;}"
        "QPushButton:checked{background:#073b5f;border-color:#00d9ff;color:#fff;}"
    )
    for section, button in getattr(window, "nav_buttons", {}).items():
        button.setFixedHeight(46)
        if section in primary:
            button.setStyleSheet(transparent)
        else:
            button.setStyleSheet(extra_style)
    spacer = getattr(window, "_v019_extra_spacer", None)
    if spacer is not None:
        spacer.setFixedHeight(640)
    footer = getattr(window, "_home_sidebar_footer", None)
    if footer is not None:
        footer.hide()
        footer.setFixedHeight(0)


def _literal_sidebar(window) -> None:
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return
    sidebar.setFixedWidth(SIDEBAR_WIDTH)
    sidebar.setStyleSheet("QFrame#sidebar{background:#03182a;border:0;border-right:1px solid #07557d;border-radius:0;}")
    _backdrop(sidebar, "v019LiteralSidebar", QRect(0, 0, SIDEBAR_WIDTH, REFERENCE_HEIGHT))
    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    if scroll is not None:
        scroll.setStyleSheet("QScrollArea#sidebarScroll{background:transparent;border:0;} QScrollArea#sidebarScroll>QWidget>QWidget{background:transparent;} QScrollBar:vertical{width:0;background:transparent;}")
        scroll.viewport().setStyleSheet("background:transparent;")
    for label in sidebar.findChildren(QLabel):
        if label.objectName() == "v019LiteralSidebar":
            continue
        label.setStyleSheet("background:transparent;color:transparent;border:0;")
    _transparent_primary_nav(window)


def _literal_topbar(window) -> None:
    top = getattr(window, "reference_top_bar", None)
    if top is None:
        return
    top.setFixedHeight(TOPBAR_HEIGHT)
    top.setStyleSheet("QFrame#referenceTopBar{background:#03182b;border:0;border-bottom:1px solid #07557d;}")
    _backdrop(top, "v019LiteralTopbar", QRect(SIDEBAR_WIDTH, 0, REFERENCE_WIDTH-SIDEBAR_WIDTH, TOPBAR_HEIGHT))
    search = getattr(top, "search", None)
    if isinstance(search, QLineEdit):
        search.setStyleSheet(
            "QLineEdit{background:transparent;color:transparent;border:0;padding:0;}"
            "QLineEdit:focus{background:rgba(3,24,43,235);color:#ffffff;border:1px solid #00c9ff;"
            "border-radius:12px;padding:0 16px;font-size:13px;}"
        )
        search.setPlaceholderText("")
    bell = getattr(top, "bell", None)
    if isinstance(bell, QPushButton):
        bell.setStyleSheet("QPushButton{background:transparent;color:transparent;border:0;}")
    for child in top.findChildren(QLabel):
        if child.objectName() == "v019LiteralTopbar":
            continue
        child.setStyleSheet("background:transparent;color:transparent;border:0;")
    for child in top.findChildren(QWidget):
        if child is top or child.objectName() == "v019LiteralTopbar" or isinstance(child, (QLineEdit, QPushButton, QLabel)):
            continue
        child.setStyleSheet("background:transparent;border:0;")


def _home_hitboxes(window, page: QWidget) -> None:
    from monitor_noticias.ui.sections import Section

    specs = (
        (Section.NEWS,          14, 166, 143, 150),
        (Section.VIDEOS,       165,166, 138, 150),
        (Section.DEMANDS,      313,166, 141, 150),
        (Section.SOURCES,      463,166, 140, 150),
        (Section.TERMS,        613,166, 141, 150),
        (Section.COVERS,       763,166, 140, 150),
        (Section.PDF_EDITOR,   913,166, 141, 150),
        (Section.EXTRACTOR,   1063,166, 177, 150),
        (Section.VIDEO_EDITOR,1248,166, 160, 150),
    )
    buttons = getattr(page, "_v019_literal_hitboxes", None)
    if buttons is None:
        buttons = []
        for section, x, y, w, h in specs:
            b = QPushButton(page)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setToolTip(section.value.label)
            b.setStyleSheet("QPushButton{background:transparent;border:0;color:transparent;} QPushButton:hover{background:rgba(0,210,255,18);border:1px solid rgba(0,210,255,45);border-radius:10px;}")
            b.clicked.connect(lambda _=False, s=section: window.navigate(s))
            buttons.append((b, x, y, w, h))
        page._v019_literal_hitboxes = buttons

    def place():
        sx = page.width() / float(REFERENCE_WIDTH - SIDEBAR_WIDTH)
        sy = page.height() / float(REFERENCE_HEIGHT - TOPBAR_HEIGHT)
        for b, x, y, w, h in buttons:
            b.setGeometry(round(x*sx), round(y*sy), max(1,round(w*sx)), max(1,round(h*sy)))
            b.show(); b.raise_()
    place()


class _HomeResizeFilter(QObject):
    def __init__(self, window, page: QWidget, backdrop: QLabel) -> None:
        super().__init__(page)
        self.window = window; self.page = page; self.backdrop = backdrop
    def eventFilter(self, obj, event):
        if obj is self.page and event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self.backdrop.setGeometry(self.page.rect())
            _home_hitboxes(self.window, self.page)
        return False


def _literal_home(window) -> None:
    from monitor_noticias.ui.sections import Section
    page = getattr(window, "pages", {}).get(Section.HOME)
    if page is None:
        return
    scroll = page.findChild(QScrollArea, "referenceHomeScroll")
    if scroll is not None:
        scroll.hide()
    backdrop = _backdrop(
        page,
        "v019LiteralHome",
        QRect(SIDEBAR_WIDTH, TOPBAR_HEIGHT, REFERENCE_WIDTH-SIDEBAR_WIDTH, REFERENCE_HEIGHT-TOPBAR_HEIGHT),
    )
    if getattr(page, "_v019_home_resize_filter", None) is None:
        filt = _HomeResizeFilter(window, page, backdrop)
        page.installEventFilter(filt)
        page._v019_home_resize_filter = filt
    _home_hitboxes(window, page)


def _apply(window) -> None:
    _literal_sidebar(window)
    _literal_topbar(window)
    _literal_home(window)
    header = getattr(window, "header_widget", None)
    if header is not None:
        header.hide(); header.setMaximumHeight(0)
    footer = getattr(window, "footer_widget", None)
    if footer is not None:
        footer.hide(); footer.setMaximumHeight(0)
    content_layout = getattr(window, "content_layout", None)
    if content_layout is not None:
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)


def install_v019_literal_screen() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    from monitor_noticias.ui.main_window import MainWindow
    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        _apply(self)

    def navigate(self, section):
        old_nav(self, section)
        _apply(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
