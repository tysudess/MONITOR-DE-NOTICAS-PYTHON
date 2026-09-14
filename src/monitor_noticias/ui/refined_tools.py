from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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
from monitor_noticias.ui.pdf_editor_page import PdfEditorPage, PdfPreview, ReorderList


def _secondary(button: QPushButton) -> QPushButton:
    button.setProperty("secondary", True)
    return button


def _danger(button: QPushButton) -> QPushButton:
    button.setProperty("danger", True)
    return button


class RefinedPdfEditorPage(PdfEditorPage):
    """Somente reconstrói a camada visual; todo o motor permanece na classe base."""

    def _button(self, text: str, slot) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(38)
        button.clicked.connect(slot)
        return button

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        left = QFrame(); left.setObjectName("techCard"); left.setFixedWidth(205)
        ll = QVBoxLayout(left); ll.setContentsMargins(12,12,12,12); ll.setSpacing(6)
        back=_secondary(QPushButton("←  Voltar ao Monitor")); back.clicked.connect(self.back_requested.emit); ll.addWidget(back)
        ttl=QLabel("Ferramentas PDF"); ttl.setObjectName("sectionTitle"); ll.addWidget(ttl)
        tools=(
            ("▣  Arquivos", self._choose_all, "#1ea7ff"),
            ("PDF", self._choose_pdfs, "#ff5362"),
            ("✂  Cortar", self._start_crop, "#a95dff"),
            ("▧  Redimensionar", self._resize_visual, "#ff5362"),
            ("▤  Criar", self._create_blank, "#32c5ff"),
            ("▣  Excluir", self._delete, "#ff5362"),
            ("▨  Capa", self._change_cover, "#16dc94"),
            ("↕  Ordenar", self._focus_reorder, "#22d9d7"),
        )
        for text,slot,color in tools:
            b=_secondary(QPushButton(text)); b.setMinimumHeight(42); b.setStyleSheet(f"QPushButton{{text-align:left;color:#f4f8fc;border-left:3px solid {color};}}")
            b.clicked.connect(slot); ll.addWidget(b)
        ll.addStretch()
        drop=QFrame(); drop.setStyleSheet("QFrame{border:1px dashed #3ab7ed;border-radius:8px;background:#052844;}")
        dl=QVBoxLayout(drop); cloud=QLabel("☁"); cloud.setAlignment(Qt.AlignmentFlag.AlignCenter); cloud.setStyleSheet("color:#67cdf5;font-size:26px;"); dl.addWidget(cloud); txt=QLabel("Arraste PDF/imagem\nou selecione"); txt.setAlignment(Qt.AlignmentFlag.AlignCenter); txt.setObjectName("smallText"); dl.addWidget(txt); sel=QPushButton("Selecionar"); sel.clicked.connect(self._choose_all); dl.addWidget(sel); ll.addWidget(drop)
        root.addWidget(left)

        center=QFrame(); center.setObjectName("techCard"); cl=QVBoxLayout(center); cl.setContentsMargins(14,12,14,12); cl.setSpacing(8)
        heading=QHBoxLayout(); hb=QVBoxLayout(); title=QLabel("Visualização do documento"); title.setObjectName("sectionTitle"); sub=QLabel("Adicione uma imagem ou PDF para começar a editar."); sub.setObjectName("smallText"); hb.addWidget(title); hb.addWidget(sub); heading.addLayout(hb,1)
        self.thumb_mode=_secondary(QPushButton("▦  Miniaturas")); self.thumb_mode.clicked.connect(lambda:self._set_list_mode(True)); self.list_mode=_secondary(QPushButton("☷  Lista")); self.list_mode.clicked.connect(lambda:self._set_list_mode(False)); heading.addWidget(self.thumb_mode); heading.addWidget(self.list_mode); cl.addLayout(heading)
        controls=QHBoxLayout(); minus=_secondary(QPushButton("−")); minus.clicked.connect(lambda:self._zoom(-.15)); controls.addWidget(minus); self.zoom_label=QLabel("100%"); self.zoom_label.setObjectName("smallTitle"); controls.addWidget(self.zoom_label); plus=_secondary(QPushButton("+")); plus.clicked.connect(lambda:self._zoom(.15)); controls.addWidget(plus); fit=_secondary(QPushButton("⛶  Ajustar")); fit.clicked.connect(lambda:self._set_zoom(1.0)); controls.addWidget(fit); undo=_secondary(QPushButton("↶")); undo.clicked.connect(self._undo); redo=_secondary(QPushButton("↷")); redo.clicked.connect(self._redo); clear=_secondary(QPushButton("▱  Limpar")); clear.clicked.connect(self._clear); controls.addWidget(undo); controls.addWidget(redo); controls.addWidget(clear); controls.addStretch(); self.page_count=QLabel("0 páginas"); self.page_count.setObjectName("smallText"); controls.addWidget(self.page_count); cl.addLayout(controls)
        body=QHBoxLayout(); self.preview=PdfPreview(); self.preview.setStyleSheet("border:1px dashed #36b7ef;border-radius:10px;background:#05213a;"); self.preview.crop_selected.connect(self._crop_done); body.addWidget(self.preview,1); self.thumbs=ReorderList(); self.thumbs.setFixedWidth(112); self.thumbs.currentRowChanged.connect(self._select); self.thumbs.reorder_requested.connect(self._reorder); body.addWidget(self.thumbs); cl.addLayout(body,1); self.status=QLabel(""); self.status.setObjectName("smallText"); cl.addWidget(self.status); root.addWidget(center,1)

        right=QFrame(); right.setObjectName("techCard"); right.setFixedWidth(275); rl=QVBoxLayout(right); rl.setContentsMargins(14,12,14,12); rl.setSpacing(9); rt=QLabel("▣  Capa e Exportação"); rt.setObjectName("sectionTitle"); rl.addWidget(rt); self.include_cover=QCheckBox("Incluir capa padrão"); self.include_cover.setChecked(True); rl.addWidget(self.include_cover)
        coverbox=QFrame(); coverbox.setStyleSheet("QFrame{background:#073252;border:1px solid #0a81b0;border-radius:9px;}"); cbl=QVBoxLayout(coverbox); self.cover=QLabel(); self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter); self.cover.setMinimumHeight(270); cbl.addWidget(self.cover); rl.addWidget(coverbox); change=_secondary(QPushButton("▧  Trocar capa")); change.clicked.connect(self._change_cover); rl.addWidget(change); rl.addStretch(); self.export_button=QPushButton("▤   GERAR PDF"); self.export_button.setProperty("green",True); self.export_button.setMinimumHeight(62); self.export_button.clicked.connect(self._export); rl.addWidget(self.export_button); root.addWidget(right)


class RefinedExtractorPage(ExtractorPage):
    def _build_ui(self) -> None:
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(10)
        frame=QFrame(); frame.setObjectName("techCard"); fl=QVBoxLayout(frame); fl.setContentsMargins(18,14,18,14); fl.setSpacing(10)
        head=QHBoxLayout(); gold=QLabel("━━"); gold.setStyleSheet("color:#ffc21a;font-size:16px;font-weight:900;"); head.addWidget(gold); titles=QVBoxLayout(); t=QLabel("EXTRATOR DE VÍDEOS"); t.setStyleSheet("color:#ffffff;font-size:27px;font-weight:900;"); s=QLabel("Fluxo direto Windows Portable v3.0.1 integrado ao Monitor"); s.setStyleSheet("color:#51c7f1;font-size:12px;"); titles.addWidget(t); titles.addWidget(s); head.addLayout(titles,1); back=_secondary(QPushButton("←  Voltar ao Monitor")); back.setProperty("gold",True); back.setEnabled(False); back.setToolTip("Representação visual da referência; a navegação funcional existente permanece na barra lateral."); head.addWidget(back); fl.addLayout(head)
        self.tabs=QTabBar();
        for label in ("⇩  Download","↺  Histórico","⚙  Configurações"): self.tabs.addTab(label)
        self.tabs.currentChanged.connect(self._switch_tab); fl.addWidget(self.tabs)
        self.stack=QStackedWidget(); self.stack.addWidget(self._build_download_tab()); self.stack.addWidget(self._build_history_tab()); self.stack.addWidget(self._build_settings_tab()); fl.addWidget(self.stack,1); root.addWidget(frame,1)

    def _build_download_tab(self) -> QWidget:
        page=QWidget(); layout=QVBoxLayout(page); layout.setContentsMargins(8,6,8,8); layout.setSpacing(9)
        label=QLabel("URL DO VÍDEO"); label.setStyleSheet("color:#77d3f7;font-size:11px;font-weight:700;"); layout.addWidget(label)
        self.url=QLineEdit(); self.url.setPlaceholderText("🔗   https://..."); self.url.returnPressed.connect(self.start_download); layout.addWidget(self.url)
        ql=QLabel("QUALIDADE DO VÍDEO"); ql.setStyleSheet("color:#77d3f7;font-size:11px;font-weight:700;"); layout.addWidget(ql)
        from PySide6.QtWidgets import QButtonGroup
        self.quality_group=QButtonGroup(self); self.quality_buttons=[]; selected=self.state_store.load_quality_index(1)
        for index,quality in enumerate(EXTRACTOR_QUALITIES):
            radio=QRadioButton(quality.label); self.quality_group.addButton(radio,index); self.quality_buttons.append(radio); radio.toggled.connect(lambda checked,i=index:self._quality_changed(i) if checked else None); layout.addWidget(radio)
        self.quality_buttons[selected].setChecked(True)
        fmt=QLabel("Formato de saída: MP4"); fmt.setObjectName("smallText"); layout.addWidget(fmt)
        self.download_button=QPushButton("⇩   BAIXAR VÍDEO"); self.download_button.setProperty("gold",True); self.download_button.setStyleSheet("QPushButton{background:#dba600;color:#07182a;border:1px solid #ffd33d;border-radius:15px;font-size:18px;font-weight:900;min-height:52px;} QPushButton:hover{background:#ffc21a;}"); self.download_button.clicked.connect(self.start_download); layout.addWidget(self.download_button)
        actions=QHBoxLayout(); self.open_videos_button=_secondary(QPushButton("▣  Abrir Vídeos")); self.open_videos_button.clicked.connect(self.open_videos); self.cancel_button=_danger(QPushButton("CANCELAR")); self.cancel_button.setEnabled(False); self.cancel_button.clicked.connect(self.cancel_download); actions.addWidget(self.open_videos_button); actions.addWidget(self.cancel_button); actions.addStretch(); layout.addLayout(actions)
        self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); self.percent=QLabel("0%"); self.percent.setObjectName("smallText"); self.status=QLabel("Cole o link, escolha a qualidade e clique em BAIXAR VÍDEO."); self.status.setWordWrap(True); self.status.setObjectName("smallText"); self.binary_status=QLabel(); self.binary_status.setObjectName("smallText"); layout.addWidget(self.progress); row=QHBoxLayout(); row.addWidget(self.percent); row.addWidget(self.status,1); layout.addLayout(row); layout.addWidget(self.binary_status); layout.addStretch(); return page

    def _build_history_tab(self) -> QWidget:
        page=QWidget(); layout=QVBoxLayout(page); top=QHBoxLayout(); title=QLabel("HISTÓRICO"); title.setObjectName("sectionTitle"); top.addWidget(title); top.addStretch(); self.clear_history_button=_danger(QPushButton("▣  LIMPAR HISTÓRICO")); self.clear_history_button.clicked.connect(self.clear_history); top.addWidget(self.clear_history_button); layout.addLayout(top); self.history=QListWidget(); layout.addWidget(self.history,1); return page

    def _build_settings_tab(self) -> QWidget:
        page=QWidget(); layout=QVBoxLayout(page); title=QLabel("CONFIGURAÇÕES"); title.setObjectName("sectionTitle"); layout.addWidget(title); gp=QFrame(); gp.setObjectName("techCard"); gl=QVBoxLayout(gp); sub=QLabel("Globoplay"); sub.setObjectName("sectionTitle"); gl.addWidget(sub); self.session_status=QLabel(); self.session_status.setObjectName("smallText"); gl.addWidget(self.session_status); row=QHBoxLayout(); self.login_button=QPushButton("LOGIN GLOBOPLAY"); self.login_button.clicked.connect(self.open_globoplay_login); self.delete_session_button=_danger(QPushButton("APAGAR SESSÃO")); self.delete_session_button.clicked.connect(self.delete_session); row.addWidget(self.login_button); row.addWidget(self.delete_session_button); row.addStretch(); gl.addLayout(row); help_text=QLabel("O login usa o helper oficial empacotado da release. A senha não é armazenada; somente os cookies da sessão são protegidos pelo Windows."); help_text.setWordWrap(True); help_text.setObjectName("smallText"); gl.addWidget(help_text); layout.addWidget(gp); yd=QFrame(); yd.setObjectName("techCard"); yl=QVBoxLayout(yd); yy=QLabel("yt-dlp"); yy.setObjectName("sectionTitle"); yl.addWidget(yy); self.update_button=QPushButton("ATUALIZAR YT-DLP"); self.update_button.clicked.connect(self.update_ytdlp); yl.addWidget(self.update_button,0,Qt.AlignmentFlag.AlignLeft); self.settings_status=QLabel(); self.settings_status.setWordWrap(True); self.settings_status.setObjectName("smallText"); yl.addWidget(self.settings_status); layout.addWidget(yd); layout.addStretch(); return page
