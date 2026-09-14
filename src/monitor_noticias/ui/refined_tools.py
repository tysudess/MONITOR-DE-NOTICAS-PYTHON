from __future__ import annotations

from PySide6.QtCore import QSize, QThread, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from monitor_noticias.extractor import EXTRACTOR_QUALITIES
from monitor_noticias.ui.extractor_page import ExtractorPage
from monitor_noticias.ui.pdf_editor_page import (
    PdfEditorPage,
    PdfPreview,
    ReorderList,
    _ImageWorker,
)


def _secondary(button: QPushButton) -> QPushButton:
    button.setProperty("secondary", True)
    return button


def _danger(button: QPushButton) -> QPushButton:
    button.setProperty("danger", True)
    return button


class RefinedPdfEditorPage(PdfEditorPage):
    """Reconstrói somente a camada visual; o PdfEditorModel permanece intacto."""

    def _button(self, text: str, slot) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(38)
        button.clicked.connect(slot)
        return button

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        left = QFrame()
        left.setObjectName("techCard")
        left.setFixedWidth(190)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(11, 11, 11, 11)
        ll.setSpacing(6)
        back = _secondary(QPushButton("←  Voltar ao Monitor"))
        back.clicked.connect(self.back_requested.emit)
        ll.addWidget(back)
        title = QLabel("Ferramentas PDF")
        title.setObjectName("sectionTitle")
        ll.addWidget(title)
        tools = (
            ("▣  Arquivos", self._choose_all, "#1ea7ff"),
            ("PDF", self._choose_pdfs, "#ff5362"),
            ("✂  Cortar", self._start_crop, "#a95dff"),
            ("▧  Redimensionar", self._resize_visual, "#ff5362"),
            ("▤  Criar", self._create_blank, "#32c5ff"),
            ("▣  Excluir", self._delete, "#ff5362"),
            ("▨  Capa", self._change_cover, "#16dc94"),
            ("↕  Ordenar", self._focus_reorder, "#22d9d7"),
        )
        for text, slot, color in tools:
            button = _secondary(QPushButton(text))
            button.setMinimumHeight(40)
            button.setStyleSheet(
                f"QPushButton{{text-align:left;color:#f4f8fc;border-left:3px solid {color};}}"
            )
            button.clicked.connect(slot)
            ll.addWidget(button)
        ll.addStretch()
        drop = QFrame()
        drop.setStyleSheet(
            "QFrame{border:1px dashed #3ab7ed;border-radius:8px;background:#052844;}"
        )
        dl = QVBoxLayout(drop)
        dl.setContentsMargins(8, 9, 8, 9)
        cloud = QLabel("☁")
        cloud.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cloud.setStyleSheet("color:#67cdf5;font-size:25px;")
        dl.addWidget(cloud)
        text = QLabel("Arraste PDF/imagem\nou selecione")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setObjectName("smallText")
        dl.addWidget(text)
        select = QPushButton("Selecionar")
        select.clicked.connect(self._choose_all)
        dl.addWidget(select)
        ll.addWidget(drop)
        root.addWidget(left)

        center = QFrame()
        center.setObjectName("techCard")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(12, 11, 12, 11)
        cl.setSpacing(7)
        heading = QHBoxLayout()
        heading_text = QVBoxLayout()
        heading_text.setSpacing(1)
        htitle = QLabel("Visualização do documento")
        htitle.setObjectName("sectionTitle")
        subtitle = QLabel("Clique em uma miniatura para trocar de página. Arraste para reordenar.")
        subtitle.setObjectName("smallText")
        heading_text.addWidget(htitle)
        heading_text.addWidget(subtitle)
        heading.addLayout(heading_text, 1)
        self.thumb_mode = _secondary(QPushButton("▦  Miniaturas"))
        self.thumb_mode.clicked.connect(lambda: self._set_list_mode(True))
        self.list_mode = _secondary(QPushButton("☷  Lista"))
        self.list_mode.clicked.connect(lambda: self._set_list_mode(False))
        heading.addWidget(self.thumb_mode)
        heading.addWidget(self.list_mode)
        cl.addLayout(heading)

        controls = QHBoxLayout()
        minus = _secondary(QPushButton("−"))
        minus.clicked.connect(lambda: self._zoom(-.15))
        controls.addWidget(minus)
        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("smallTitle")
        self.zoom_label.setMinimumWidth(48)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls.addWidget(self.zoom_label)
        plus = _secondary(QPushButton("+"))
        plus.clicked.connect(lambda: self._zoom(.15))
        controls.addWidget(plus)
        fit = _secondary(QPushButton("⛶  Ajustar"))
        fit.clicked.connect(lambda: self._set_zoom(1.0))
        controls.addWidget(fit)
        undo = _secondary(QPushButton("↶"))
        undo.clicked.connect(self._undo)
        redo = _secondary(QPushButton("↷"))
        redo.clicked.connect(self._redo)
        clear = _secondary(QPushButton("▱  Limpar"))
        clear.clicked.connect(self._clear)
        controls.addWidget(undo)
        controls.addWidget(redo)
        controls.addWidget(clear)
        controls.addStretch()
        self.page_count = QLabel("0 páginas")
        self.page_count.setObjectName("smallText")
        controls.addWidget(self.page_count)
        cl.addLayout(controls)

        body = QHBoxLayout()
        body.setSpacing(8)
        self.preview = PdfPreview()
        self.preview.setStyleSheet(
            "border:1px dashed #36b7ef;border-radius:10px;background:#061a2d;"
        )
        self.preview.crop_selected.connect(self._crop_done)
        body.addWidget(self.preview, 1)
        self.thumbs = ReorderList()
        self.thumbs.setFixedWidth(132)
        self.thumbs.setIconSize(QSize(82, 108))
        self.thumbs.setSpacing(5)
        self.thumbs.setStyleSheet(
            "QListWidget{background:#052844;border:1px solid #087eae;border-radius:9px;padding:5px;}"
            "QListWidget::item{background:#07395d;border:1px solid #0a6f9d;border-radius:8px;"
            "padding:5px;color:#d9efff;}"
            "QListWidget::item:selected{background:#0b6699;border:2px solid #28c4ff;color:white;}"
        )
        self.thumbs.currentRowChanged.connect(self._select)
        self.thumbs.itemClicked.connect(lambda item: self._select(self.thumbs.row(item)))
        self.thumbs.reorder_requested.connect(self._reorder)
        body.addWidget(self.thumbs)
        cl.addLayout(body, 1)
        self.status = QLabel("")
        self.status.setObjectName("smallText")
        cl.addWidget(self.status)
        root.addWidget(center, 1)

        right = QFrame()
        right.setObjectName("techCard")
        right.setFixedWidth(245)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 11, 12, 11)
        rl.setSpacing(8)
        rt = QLabel("▣  Capa e Exportação")
        rt.setObjectName("sectionTitle")
        rl.addWidget(rt)
        self.include_cover = QCheckBox("Incluir capa padrão")
        self.include_cover.setChecked(True)
        rl.addWidget(self.include_cover)
        coverbox = QFrame()
        coverbox.setStyleSheet(
            "QFrame{background:#073252;border:1px solid #0a81b0;border-radius:9px;}"
        )
        cbl = QVBoxLayout(coverbox)
        self.cover = QLabel()
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setMinimumHeight(235)
        cbl.addWidget(self.cover)
        rl.addWidget(coverbox)
        change = _secondary(QPushButton("▧  Trocar capa"))
        change.clicked.connect(self._change_cover)
        rl.addWidget(change)
        helper = QLabel("A capa é opcional. O documento mantém a ordem mostrada nas miniaturas.")
        helper.setObjectName("smallText")
        helper.setWordWrap(True)
        rl.addWidget(helper)
        rl.addStretch()
        self.export_button = QPushButton("▤   GERAR PDF")
        self.export_button.setProperty("green", True)
        self.export_button.setMinimumHeight(56)
        self.export_button.clicked.connect(self._export)
        rl.addWidget(self.export_button)
        root.addWidget(right)

    def _run_image_worker(self, token: int, fn, on_done=None) -> None:
        """Mantém somente o resultado mais novo sem invalidar a nova miniatura/preview."""
        thread = QThread(self)
        worker = _ImageWorker(token, fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        jobs = getattr(self, "_preview_jobs", None)
        if jobs is None:
            jobs = {}
            self._preview_jobs = jobs
        jobs[thread] = worker

        def done(result_token, image) -> None:
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
            jobs.pop(thread, None)
            if self._preview_thread is thread:
                self._preview_thread = None

        worker.done.connect(done)
        worker.failed.connect(failed)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(cleanup)
        thread.finished.connect(thread.deleteLater)
        self._preview_thread = thread
        thread.start()


class RefinedExtractorPage(ExtractorPage):
    """Layout refinado do Extrator; callbacks e engine continuam na classe base."""

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(9)

        tabs_card = QFrame()
        tabs_card.setObjectName("filterCard")
        tabs_layout = QVBoxLayout(tabs_card)
        tabs_layout.setContentsMargins(12, 8, 12, 8)
        tabs_layout.setSpacing(7)
        top = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Central de downloads")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Baixe, consulte o histórico e gerencie a sessão do Extrator v3.0.1.")
        subtitle.setObjectName("smallText")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        top.addLayout(title_box, 1)
        format_badge = QLabel("MP4  •  Windows Portable")
        format_badge.setStyleSheet(
            "color:#ffc21a;border:1px solid #9b7200;background:#3a3108;"
            "border-radius:7px;padding:6px 10px;font-weight:700;"
        )
        top.addWidget(format_badge)
        tabs_layout.addLayout(top)
        self.tabs = QTabBar()
        for label in ("⇩  Download", "↺  Histórico", "⚙  Configurações"):
            self.tabs.addTab(label)
        self.tabs.currentChanged.connect(self._switch_tab)
        tabs_layout.addWidget(self.tabs)
        root.addWidget(tabs_card)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_download_tab())
        self.stack.addWidget(self._build_history_tab())
        self.stack.addWidget(self._build_settings_tab())
        root.addWidget(self.stack, 1)

    def _build_download_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        url_card = QFrame()
        url_card.setObjectName("techCard")
        ul = QVBoxLayout(url_card)
        ul.setContentsMargins(16, 13, 16, 13)
        ul.setSpacing(7)
        label = QLabel("URL DO VÍDEO")
        label.setObjectName("smallTitle")
        ul.addWidget(label)
        self.url = QLineEdit()
        self.url.setPlaceholderText("🔗   Cole aqui o link do vídeo...")
        self.url.setMinimumHeight(44)
        self.url.returnPressed.connect(self.start_download)
        ul.addWidget(self.url)
        hint = QLabel("O motor aceita as mesmas URLs e regras da versão já validada.")
        hint.setObjectName("smallText")
        ul.addWidget(hint)
        layout.addWidget(url_card)

        quality_card = QFrame()
        quality_card.setObjectName("techCard")
        ql = QVBoxLayout(quality_card)
        ql.setContentsMargins(16, 12, 16, 12)
        ql.setSpacing(8)
        qhead = QHBoxLayout()
        qtitle = QLabel("QUALIDADE DO VÍDEO")
        qtitle.setObjectName("smallTitle")
        qhead.addWidget(qtitle)
        qhead.addStretch()
        fmt = QLabel("Formato de saída: MP4")
        fmt.setObjectName("smallText")
        qhead.addWidget(fmt)
        ql.addLayout(qhead)
        quality_row = QHBoxLayout()
        quality_row.setSpacing(8)
        self.quality_group = QButtonGroup(self)
        self.quality_buttons = []
        selected = self.state_store.load_quality_index(1)
        for index, quality in enumerate(EXTRACTOR_QUALITIES):
            radio = QRadioButton(quality.label)
            radio.setMinimumHeight(38)
            radio.setStyleSheet(
                "QRadioButton{background:#062e4d;border:1px solid #0a6f9d;border-radius:8px;"
                "padding:8px 12px;color:#e9f5ff;}"
                "QRadioButton:checked{background:#075c8c;border:1px solid #2bc7ff;color:white;font-weight:700;}"
            )
            self.quality_group.addButton(radio, index)
            self.quality_buttons.append(radio)
            radio.toggled.connect(
                lambda checked, i=index: self._quality_changed(i) if checked else None
            )
            quality_row.addWidget(radio, 1)
        self.quality_buttons[selected].setChecked(True)
        ql.addLayout(quality_row)
        layout.addWidget(quality_card)

        action_card = QFrame()
        action_card.setObjectName("techCard")
        al = QVBoxLayout(action_card)
        al.setContentsMargins(16, 13, 16, 13)
        al.setSpacing(8)
        self.download_button = QPushButton("⇩   BAIXAR VÍDEO")
        self.download_button.setProperty("gold", True)
        self.download_button.setStyleSheet(
            "QPushButton{background:#dba600;color:#07182a;border:1px solid #ffd33d;"
            "border-radius:10px;font-size:17px;font-weight:900;min-height:50px;}"
            "QPushButton:hover{background:#ffc21a;}"
            "QPushButton:disabled{background:#66571d;color:#a9a27e;border-color:#7c6a25;}"
        )
        self.download_button.clicked.connect(self.start_download)
        al.addWidget(self.download_button)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        al.addWidget(self.progress)
        progress_row = QHBoxLayout()
        self.percent = QLabel("0%")
        self.percent.setObjectName("smallTitle")
        progress_row.addWidget(self.percent)
        self.status = QLabel("Cole o link, escolha a qualidade e clique em BAIXAR VÍDEO.")
        self.status.setWordWrap(True)
        self.status.setObjectName("smallText")
        progress_row.addWidget(self.status, 1)
        al.addLayout(progress_row)
        actions = QHBoxLayout()
        self.open_videos_button = _secondary(QPushButton("▣  Abrir pasta de vídeos"))
        self.open_videos_button.clicked.connect(self.open_videos)
        self.cancel_button = _danger(QPushButton("■  CANCELAR"))
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)
        actions.addWidget(self.open_videos_button)
        actions.addWidget(self.cancel_button)
        actions.addStretch()
        al.addLayout(actions)
        self.binary_status = QLabel()
        self.binary_status.setObjectName("smallText")
        self.binary_status.setWordWrap(True)
        al.addWidget(self.binary_status)
        layout.addWidget(action_card)
        layout.addStretch()
        return page

    def _build_history_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)
        header = QFrame()
        header.setObjectName("filterCard")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 9, 14, 9)
        title = QLabel("Histórico de downloads")
        title.setObjectName("sectionTitle")
        hl.addWidget(title)
        hl.addStretch()
        self.clear_history_button = _danger(QPushButton("▣  Limpar histórico"))
        self.clear_history_button.clicked.connect(self.clear_history)
        hl.addWidget(self.clear_history_button)
        layout.addWidget(header)
        self.history = QListWidget()
        layout.addWidget(self.history, 1)
        return page

    def _build_settings_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        intro = QFrame()
        intro.setObjectName("filterCard")
        il = QVBoxLayout(intro)
        il.setContentsMargins(14, 9, 14, 9)
        title = QLabel("Configurações do Extrator")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Sessão Globoplay e atualização do yt-dlp sem alterar o fluxo de download.")
        subtitle.setObjectName("smallText")
        il.addWidget(title)
        il.addWidget(subtitle)
        layout.addWidget(intro)

        cards = QHBoxLayout()
        cards.setSpacing(10)
        globoplay = QFrame()
        globoplay.setObjectName("techCard")
        gl = QVBoxLayout(globoplay)
        gl.setContentsMargins(16, 13, 16, 13)
        gp_title = QLabel("Globoplay")
        gp_title.setObjectName("sectionTitle")
        gl.addWidget(gp_title)
        self.session_status = QLabel()
        self.session_status.setObjectName("smallText")
        self.session_status.setWordWrap(True)
        gl.addWidget(self.session_status)
        row = QHBoxLayout()
        self.login_button = QPushButton("LOGIN GLOBOPLAY")
        self.login_button.clicked.connect(self.open_globoplay_login)
        self.delete_session_button = _danger(QPushButton("APAGAR SESSÃO"))
        self.delete_session_button.clicked.connect(self.delete_session)
        row.addWidget(self.login_button)
        row.addWidget(self.delete_session_button)
        row.addStretch()
        gl.addLayout(row)
        help_text = QLabel(
            "A senha não é armazenada. Somente os cookies da sessão são protegidos pelo Windows."
        )
        help_text.setWordWrap(True)
        help_text.setObjectName("smallText")
        gl.addWidget(help_text)
        gl.addStretch()
        cards.addWidget(globoplay, 1)

        ytdlp = QFrame()
        ytdlp.setObjectName("techCard")
        yl = QVBoxLayout(ytdlp)
        yl.setContentsMargins(16, 13, 16, 13)
        yt_title = QLabel("yt-dlp")
        yt_title.setObjectName("sectionTitle")
        yl.addWidget(yt_title)
        yt_help = QLabel("Atualize somente o componente yt-dlp usado pelo Extrator.")
        yt_help.setObjectName("smallText")
        yt_help.setWordWrap(True)
        yl.addWidget(yt_help)
        self.update_button = QPushButton("ATUALIZAR YT-DLP")
        self.update_button.clicked.connect(self.update_ytdlp)
        yl.addWidget(self.update_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.settings_status = QLabel()
        self.settings_status.setWordWrap(True)
        self.settings_status.setObjectName("smallText")
        yl.addWidget(self.settings_status)
        yl.addStretch()
        cards.addWidget(ytdlp, 1)
        layout.addLayout(cards)
        layout.addStretch()
        return page
