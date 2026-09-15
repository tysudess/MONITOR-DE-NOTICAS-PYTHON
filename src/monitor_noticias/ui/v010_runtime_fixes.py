from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QTimer
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget

log = logging.getLogger(__name__)
_INSTALLED = False


def _proxy_url(cfg) -> str:
    if not getattr(cfg, "enabled", False) or not getattr(cfg, "host", ""):
        return ""
    host = str(cfg.host).strip()
    port = int(cfg.port)
    user = str(getattr(cfg, "username", "") or "")
    password = str(getattr(cfg, "password", "") or "")
    auth = ""
    if user and password:
        auth = f"{quote(user, safe='')}:{quote(password, safe='')}@"
    return f"http://{auth}{host}:{port}"


def _sync_proxy_environment(cfg) -> str:
    url = _proxy_url(cfg)
    keys = ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "MONITOR_PROXY_URL")
    for key in keys:
        if url:
            os.environ[key] = url
        else:
            os.environ.pop(key, None)
    return url


def _patch_global_proxy() -> None:
    from monitor_noticias.networking.proxy import ProxySettings
    from monitor_noticias.ui.refined_settings import SettingsPage

    if getattr(ProxySettings, "_v010_global_proxy_patched", False):
        return

    original_init = ProxySettings.__init__
    original_load = ProxySettings.load
    original_save = ProxySettings.save

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        try:
            _sync_proxy_environment(original_load(self))
        except Exception:
            log.exception("Falha ao aplicar proxy global na inicialização")

    def load(self):
        cfg = original_load(self)
        _sync_proxy_environment(cfg)
        return cfg

    def save(self, *args, **kwargs):
        cfg = original_save(self, *args, **kwargs)
        _sync_proxy_environment(cfg)
        return cfg

    ProxySettings.__init__ = init
    ProxySettings.load = load
    ProxySettings.save = save
    ProxySettings._v010_global_proxy_patched = True

    original_save_ui = SettingsPage._save_proxy

    def save_proxy_ui(self):
        original_save_ui(self)
        # Processos externos recebem o proxy pela variável de ambiente. Se já
        # estavam abertos, são reiniciados para herdarem a conexão única salva
        # em Configurações.
        window = self.window()
        pages = getattr(window, "pages", {})
        try:
            from monitor_noticias.ui.sections import Section
            for section in (Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION):
                page = pages.get(section)
                if page is not None and hasattr(page, "restart"):
                    page.restart()
        except Exception:
            log.exception("Falha ao reiniciar integração após alteração de proxy")

    SettingsPage._save_proxy = save_proxy_ui


def _copy_url(url: str) -> bool:
    text = str(url or "").strip()
    if not text:
        return False
    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text, QClipboard.Mode.Clipboard)
    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    return clipboard.text(QClipboard.Mode.Clipboard) == text


_vehicle_resolver = None


def _vehicle_url(url: str) -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""
    try:
        from monitor_noticias.networking.google_news_resolver import GoogleNewsUrlResolver, is_google_news
        if not is_google_news(raw):
            return raw
        global _vehicle_resolver
        if _vehicle_resolver is None:
            _vehicle_resolver = GoogleNewsUrlResolver()
        resolved = _vehicle_resolver.resolve(raw)
        if resolved and not is_google_news(resolved):
            return resolved
    except Exception:
        log.exception("Falha ao resolver link do veículo")
    return raw


def _window_for(widget: QWidget):
    window = widget.window()
    return window if window is not None else QApplication.activeWindow()


def _patch_result_cards() -> None:
    from monitor_noticias.ui.refined_cards import NewsCard, VideoCard
    from monitor_noticias.ui.refined_base import open_url, open_whatsapp, secondary

    if getattr(NewsCard, "_v010_links_patched", False):
        return

    original_news_init = NewsCard.__init__
    original_video_init = VideoCard.__init__

    def news_init(self, item, actions_enabled=True):
        original_news_init(self, item, actions_enabled)
        buttons = self.findChildren(QPushButton)
        for button in buttons:
            text = button.text()
            if "Copiar link" in text:
                try: button.clicked.disconnect()
                except Exception: pass
                button.clicked.connect(lambda _=False, i=item: _copy_url(_vehicle_url(i.link)))
            elif "Abrir matéria" in text:
                try: button.clicked.disconnect()
                except Exception: pass
                button.clicked.connect(lambda _=False, i=item: open_url(_vehicle_url(i.link)))
            elif "WhatsApp" in text:
                try: button.clicked.disconnect()
                except Exception: pass
                button.clicked.connect(lambda _=False, i=item: open_whatsapp(i.title, _vehicle_url(i.link)))
        if actions_enabled:
            action_layout = self.layout().itemAt(self.layout().count() - 1).layout()
            if action_layout is not None:
                send = secondary(QPushButton("⇩  Extrair matéria"))
                send.setToolTip("Abre o Extrator de Notícias com o link desta matéria já preenchido.")
                send.clicked.connect(lambda _=False, i=item, w=self: getattr(_window_for(w), "send_news_to_extractor", lambda _u: None)(_vehicle_url(i.link)))
                action_layout.addWidget(send)

    def video_init(self, item, actions_enabled=True):
        original_video_init(self, item, actions_enabled)
        for button in self.findChildren(QPushButton):
            if "Copiar link" in button.text():
                try: button.clicked.disconnect()
                except Exception: pass
                button.clicked.connect(lambda _=False, i=item: _copy_url(i.link))
        if actions_enabled:
            action_layout = self.layout().itemAt(self.layout().count() - 1).layout()
            if action_layout is not None:
                send = secondary(QPushButton("⇩  Extrair vídeo"))
                send.setToolTip("Abre o Extrator de Vídeos com este link já preenchido.")
                send.clicked.connect(lambda _=False, i=item, w=self: getattr(_window_for(w), "send_video_to_extractor", lambda _u: None)(i.link))
                action_layout.addWidget(send)

    NewsCard.__init__ = news_init
    VideoCard.__init__ = video_init
    NewsCard._v010_links_patched = True
    VideoCard._v010_links_patched = True


def _patch_external_paste() -> None:
    from monitor_noticias.ui.external_win32_page import ExternalWin32AppPage

    if getattr(ExternalWin32AppPage, "_v010_paste_patched", False):
        return
    original_poll = ExternalWin32AppPage._poll

    def _inject(self) -> bool:
        value = str(getattr(self, "_pending_monitor_url", "") or "").strip()
        if not value or os.name != "nt" or not getattr(self, "_hwnd", 0):
            return False
        _copy_url(value)
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            candidates: list[int] = []
            cb_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

            @cb_type
            def enum_child(hwnd, _param):
                buf = ctypes.create_unicode_buffer(128)
                user32.GetClassNameW(hwnd, buf, len(buf))
                cls = buf.value.casefold()
                if "edit" in cls or "entry" in cls:
                    candidates.append(int(hwnd))
                return True

            user32.EnumChildWindows(int(self._hwnd), enum_child, 0)
            WM_SETTEXT = 0x000C
            for hwnd in candidates:
                user32.SendMessageW(hwnd, WM_SETTEXT, 0, value)
                length = user32.GetWindowTextLengthW(hwnd)
                if length:
                    check = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, check, len(check))
                    if check.value.strip() == value:
                        self._pending_monitor_url = ""
                        self.status.setText("● Link recebido do Monitor")
                        return True
        except Exception:
            log.exception("Falha ao preencher link na integração externa")
        return False

    def set_url_and_paste(self, url: str) -> None:
        self._pending_monitor_url = str(url or "").strip()
        if self._process is None:
            self.start()
        for delay in (0, 250, 700, 1400, 2500):
            QTimer.singleShot(delay, lambda s=self: _inject(s))

    def poll(self):
        original_poll(self)
        if getattr(self, "_pending_monitor_url", "") and getattr(self, "_hwnd", 0):
            _inject(self)

    ExternalWin32AppPage.set_url_and_paste = set_url_and_paste
    ExternalWin32AppPage._poll = poll
    ExternalWin32AppPage._v010_paste_patched = True


def _patch_pdf_preview_threads() -> None:
    from monitor_noticias.ui.pdf_editor_page import PdfEditorPage, _ImageWorker
    from PySide6.QtCore import QThread
    from PySide6.QtGui import QImage

    if getattr(PdfEditorPage, "_v010_preview_thread_patched", False):
        return

    def run_image_worker(self, token: int, fn, on_done=None) -> None:
        # Mantém referências de TODOS os jobs até o término. A implementação
        # anterior sobrescrevia _preview_thread/_preview_worker ao importar uma
        # imagem enquanto outra prévia ainda renderizava, cenário que podia
        # destruir um QThread ativo e encerrar todo o processo Qt.
        jobs = getattr(self, "_v010_preview_jobs", None)
        if jobs is None:
            jobs = []
            self._v010_preview_jobs = jobs
        thread = QThread(self)
        worker = _ImageWorker(token, fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        job = (thread, worker)
        jobs.append(job)

        def done(result_token: int, image: QImage) -> None:
            if result_token == self._preview_token:
                if on_done:
                    on_done(image)
                else:
                    self.preview.set_image(image, self.model.zoom, None)
            thread.quit()

        def failed(result_token: int, message: str) -> None:
            if result_token == self._preview_token:
                self.status.setText(message)
            thread.quit()

        def cleanup() -> None:
            try:
                jobs.remove(job)
            except ValueError:
                pass
            if getattr(self, "_preview_thread", None) is thread:
                self._preview_thread = None
                self._preview_worker = None

        worker.done.connect(done)
        worker.failed.connect(failed)
        thread.finished.connect(cleanup)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._preview_thread = thread
        self._preview_worker = worker
        thread.start()

    PdfEditorPage._run_image_worker = run_image_worker
    PdfEditorPage._v010_preview_thread_patched = True


def _patch_video_sequence_transition() -> None:
    from monitor_noticias.ui.integrated_tools import OriginalVideoEditorPage
    try:
        from PySide6.QtMultimedia import QMediaPlayer
    except Exception:
        return

    if getattr(OriginalVideoEditorPage, "_v010_sequence_patched", False):
        return
    original_init = OriginalVideoEditorPage.__init__

    def init(self, app_root):
        original_init(self, app_root)
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        editor._v010_switch_pending = False

        def next_boundary() -> None:
            if not getattr(editor, "sequence_playing", False) or getattr(editor, "_v010_switch_pending", False):
                return
            idx = int(getattr(editor, "preview_clip_index", getattr(editor, "selected_index", -1)))
            clips = getattr(editor, "clips", [])
            if not (0 <= idx < len(clips) - 1):
                return
            editor._v010_switch_pending = True
            boundary = 0
            for clip in clips[: idx + 1]:
                boundary += max(0, int(clip.get("end_ms", 0)) - int(clip.get("start_ms", 0)))

            def do_switch():
                try:
                    editor.seek_sequence(boundary, True)
                finally:
                    QTimer.singleShot(350, lambda: setattr(editor, "_v010_switch_pending", False))
            QTimer.singleShot(0, do_switch)

        def position_changed(position: int) -> None:
            if not getattr(editor, "sequence_playing", False):
                return
            end = int(getattr(editor, "preview_clip_end_source_ms", 0) or 0)
            if end and int(position) >= max(0, end - 45):
                next_boundary()

        def status_changed(status) -> None:
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                next_boundary()

        editor.player.positionChanged.connect(position_changed)
        editor.player.mediaStatusChanged.connect(status_changed)

    OriginalVideoEditorPage.__init__ = init
    OriginalVideoEditorPage._v010_sequence_patched = True


def _group_header(text: str) -> QWidget:
    from PySide6.QtWidgets import QHBoxLayout
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(16, 10, 8, 4)
    row.setSpacing(9)
    dash = QLabel("━")
    dash.setStyleSheet("color:#ffc21a;font-size:18px;font-weight:900;")
    title = QLabel(text)
    title.setObjectName("sideGroupTitle")
    row.addWidget(dash)
    row.addWidget(title)
    row.addStretch(1)
    return box


def _patch_sidebar_reference() -> None:
    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section

    if getattr(MainWindow, "_v010_sidebar_reference_patched", False):
        return
    original_build = MainWindow._build_ui
    original_navigate = MainWindow.navigate

    groups = (
        ("PRINCIPAL", Section.HOME),
        ("GERENCIAMENTO", Section.DEMANDS),
        ("FERRAMENTAS", Section.PDF_EDITOR),
        ("SISTEMA", Section.SETTINGS),
    )

    def build(self):
        original_build(self)
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet((self.sidebar.styleSheet() or "") + """
            QFrame#sidebar { border-radius:0px; border-left:2px solid #0a9ed7; }
            QLabel#sideGroupTitle { color:#82aeda; font-size:12px; font-weight:800; letter-spacing:1px; }
            QPushButton#navButton { min-height:48px; font-size:15px; padding:8px 10px; border:1px solid transparent; }
            QPushButton#navButton:checked { border:1px solid #09b5ff; border-radius:10px; background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #087bc5,stop:1 #064a7b); }
            QFrame#sideStatusCard { border:1px solid #078dc8; border-radius:11px; background:#052d4a; }
        """)
        anchor = self.sidebar.findChild(QLabel, "anchorMark")
        if anchor is not None:
            anchor.setFixedSize(66, 66)
            anchor.setStyleSheet("color:#ffc21a;font-size:39px;font-weight:800;border:1px solid #078bc8;border-radius:10px;background:#05375b;")
        # Insere os títulos exatamente antes do primeiro item de cada grupo.
        any_holder = next(iter(self.nav_holders.values()), None)
        layout = any_holder.parentWidget().layout() if any_holder is not None else None
        if layout is not None:
            for title, first in groups:
                holder = self.nav_holders[first]
                index = layout.indexOf(holder)
                if index >= 0:
                    layout.insertWidget(index, _group_header(title))
            # Linha/nós visuais à esquerda de cada item, como na referência.
            for holder in self.nav_holders.values():
                row = holder.layout()
                if row is not None:
                    node = QLabel("●")
                    node.setFixedWidth(13)
                    node.setAlignment(node.alignment())
                    node.setStyleSheet("color:#35bfff;font-size:12px;border-left:1px solid #149bd4;")
                    row.insertWidget(0, node)
        self.side_status_title.setText("●   Busca em andamento")

    def navigate(self, section):
        original_navigate(self, section)
        for sec, button in self.nav_buttons.items():
            base = f"{sec.value.icon}   {sec.value.label}"
            button.setText(base + ("      ❯" if sec == section else ""))

    def send_video_to_extractor(self, url: str) -> None:
        self.navigate(Section.EXTRACTOR)
        page = self.pages.get(Section.EXTRACTOR)
        field = getattr(page, "url", None)
        if field is not None:
            field.setText(str(url or ""))
            field.setFocus()
            tabs = getattr(page, "tabs", None)
            if tabs is not None:
                tabs.setCurrentIndex(0)

    def send_news_to_extractor(self, url: str) -> None:
        self.navigate(Section.NEWS_EXTRACTOR)
        page = self.pages.get(Section.NEWS_EXTRACTOR)
        if page is not None and hasattr(page, "set_url_and_paste"):
            page.set_url_and_paste(str(url or ""))

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
    MainWindow.send_video_to_extractor = send_video_to_extractor
    MainWindow.send_news_to_extractor = send_news_to_extractor
    MainWindow._v010_sidebar_reference_patched = True


def install_v010_runtime_fixes() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    _patch_global_proxy()
    _patch_external_paste()
    _patch_pdf_preview_threads()
    _patch_video_sequence_transition()
    _patch_result_cards()
    _patch_sidebar_reference()
