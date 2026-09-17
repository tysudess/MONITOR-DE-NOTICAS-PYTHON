from __future__ import annotations

"""v0.0.19 — aba Notícias no padrão visual da referência aprovada.

Mantém o motor, controller e modelos existentes. Esta camada apenas substitui a
composição visual da NewsPage refinada e acrescenta ordenação/paginação local.
"""

import math

from PySide6.QtCore import QDate, QPointF, QRectF, Qt, QTime
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QPushButton, QScrollArea, QTimeEdit, QVBoxLayout, QWidget,
)

from monitor_noticias.ui.refined_base import BasePage, copy_text, duration, format_time, open_url, open_whatsapp

_INSTALLED = False


NEWS_STYLE = """
QWidget#newsReferencePage { background:#03182a; }
QFrame#newsHero, QFrame#newsFilter, QFrame#newsExec, QFrame#newsMetrics, QFrame#newsRow {
    background:#051f36; border:1px solid #0b628d; border-radius:12px;
}
QFrame#newsHero { background:#041b31; }
QLabel#newsEyebrow { color:#25b9ff; font-size:11px; font-weight:800; letter-spacing:1px; }
QLabel#newsHeroTitle { color:#ffffff; font-size:36px; font-weight:900; }
QLabel#newsHeroSub { color:#d5e6f4; font-size:15px; }
QLabel#newsSectionTitle { color:#ffffff; font-size:17px; font-weight:900; }
QLabel#newsMuted { color:#a7bfd3; font-size:11px; }
QLabel#newsMeta { color:#4fc8ff; font-size:11px; }
QLabel#newsCardTitle { color:#ffffff; font-size:13px; font-weight:800; }
QLabel#newsSnippet { color:#b7c9d8; font-size:10px; }
QLineEdit#newsSearch {
    background:#061d33; color:#eaf6ff; border:1px solid #168fd0; border-radius:10px;
    min-height:42px; padding:0 14px; font-size:12px;
}
QPushButton#newsPrimary {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #087cf3,stop:1 #0a52ff);
    color:white; border:1px solid #19c8ff; border-radius:9px; min-height:42px;
    padding:0 20px; font-weight:800;
}
QPushButton#newsPrimary:hover { background:#0b73e9; }
QPushButton#newsPeriod {
    background:#06223b; color:#eaf5ff; border:1px solid #0d6090; border-radius:8px;
    min-height:34px; padding:0 18px; font-weight:700;
}
QPushButton#newsPeriod:checked { border:1px solid #00d7ff; background:#075188; }
QPushButton#newsAction {
    background:#06243f; color:#f2f8ff; border:1px solid #168cca; border-radius:8px;
    min-height:34px; padding:0 14px; font-weight:700;
}
QPushButton#newsWhatsApp { background:#074a3f; color:white; border:1px solid #19c88d; border-radius:8px; min-height:34px; padding:0 14px; font-weight:800; }
QPushButton#newsExtract { background:#281d4a; color:#f4e8ff; border:1px solid #9a5df1; border-radius:8px; min-height:34px; padding:0 14px; font-weight:800; }
QPushButton#newsExtract:disabled { color:#806f9b; border-color:#55456f; background:#1b1730; }
QPushButton#newsPager { background:#06243f; color:#eaf5ff; border:1px solid #0e567f; border-radius:8px; min-width:38px; min-height:34px; }
QPushButton#newsPager:disabled { color:#3e5f74; border-color:#17394d; }
QCheckBox { color:#eaf5ff; spacing:8px; }
QCheckBox::indicator { width:18px; height:18px; border:1px solid #1785bd; border-radius:4px; background:#041b31; }
QCheckBox::indicator:checked { background:#0a7ef2; border-color:#25d5ff; }
QComboBox { background:#06243f; color:#eaf5ff; border:1px solid #0d6090; border-radius:8px; min-height:34px; padding:0 10px; }
QProgressBar { background:#06223a; border:0; border-radius:5px; min-height:9px; max-height:9px; }
QProgressBar::chunk { background:#1edba8; border-radius:5px; }
QScrollArea#newsScroll { background:transparent; border:0; }
QScrollArea#newsScroll > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { background:#03182a; width:8px; border:0; }
QScrollBar::handle:vertical { background:#0b628d; min-height:32px; border-radius:4px; }
"""


class _NewsHero(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("newsHero")
        self.setFixedHeight(144)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(1)
        eye = QLabel("CENTRAL DE INTELIGÊNCIA DE MÍDIA")
        eye.setObjectName("newsEyebrow")
        title = QLabel("Notícias")
        title.setObjectName("newsHeroTitle")
        sub = QLabel("Acompanhe matérias em tempo real e transforme\ninformação em decisões estratégicas.")
        sub.setObjectName("newsHeroSub")
        lay.addWidget(eye)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h = self.width(), self.height()
        grad = QLinearGradient(w * .30, 0, w * .88, h)
        grad.setColorAt(0, QColor(0, 45, 88, 0))
        grad.setColorAt(.55, QColor(0, 103, 180, 80))
        grad.setColorAt(1, QColor(0, 31, 61, 10))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 11, 11)
        cx, cy, r = w * .51, h * .70, h * .92
        p.setBrush(QColor(0, 62, 118, 118))
        p.setPen(QPen(QColor(0, 195, 255, 145), 1))
        p.drawEllipse(QPointF(cx, cy), r, r)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for f in (.35, .62, .84):
            p.setPen(QPen(QColor(23, 180, 255, 70), 1))
            p.drawEllipse(QRectF(cx-r*.92, cy-r*f*.40, r*1.84, r*f*.80))
        p.setPen(QPen(QColor(0, 217, 255, 150), 1))
        for dx in (-.55, -.2, .22, .56):
            p.drawLine(QPointF(cx + r*dx, cy-r*.70), QPointF(cx + r*dx*.28, cy+r*.70))
        p.end()


class _Metric(QFrame):
    def __init__(self, icon: str, caption: str, color: str) -> None:
        super().__init__()
        box = QVBoxLayout(self)
        box.setContentsMargins(10, 7, 10, 7)
        box.setSpacing(0)
        self.icon = QLabel(icon)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet(f"color:{color};font-size:18px;")
        self.value = QLabel("0")
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value.setStyleSheet(f"color:{color};font-size:18px;font-weight:900;")
        cap = QLabel(caption)
        cap.setObjectName("newsMuted")
        cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.icon)
        box.addWidget(self.value)
        box.addWidget(cap)


class _ReferenceNewsCard(QFrame):
    COLORS = ("#21b8ff", "#b256ff", "#ffc43d", "#27daa1")

    def __init__(self, item, index: int) -> None:
        super().__init__()
        self.setObjectName("newsRow")
        self.setMinimumHeight(72)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 6, 12, 6)
        row.setSpacing(10)
        stripe = QFrame(); stripe.setFixedWidth(6); stripe.setStyleSheet(f"background:{self.COLORS[index % len(self.COLORS)]};border-radius:3px;")
        row.addWidget(stripe)
        icon = QLabel("▤"); icon.setFixedSize(45,45); icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"color:{self.COLORS[index % len(self.COLORS)]};background:#0a3151;border-radius:8px;font-size:20px;font-weight:900;")
        row.addWidget(icon)
        text = QVBoxLayout(); text.setSpacing(1)
        meta = QLabel(f"{getattr(item,'source','')}  •  {format_time(getattr(item,'date',0))}")
        meta.setObjectName("newsMeta"); text.addWidget(meta)
        title = QLabel(getattr(item,"title","") or "—"); title.setObjectName("newsCardTitle"); title.setWordWrap(False); text.addWidget(title)
        snippet_text = getattr(item,"snippet","") or ""
        if snippet_text:
            snippet = QLabel(snippet_text); snippet.setObjectName("newsSnippet"); snippet.setWordWrap(False); text.addWidget(snippet)
        row.addLayout(text, 1)
        tag_text = getattr(item,"matchedDemand","") or getattr(item,"matchedTerm","") or ""
        if tag_text:
            tag = QLabel(str(tag_text).upper()[:18]); tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tag.setStyleSheet("color:#59caff;border:1px solid #167cb2;border-radius:9px;padding:4px 10px;font-size:9px;font-weight:800;")
            row.addWidget(tag)
        open_btn = QPushButton("↗  Abrir matéria"); open_btn.setObjectName("newsAction"); open_btn.clicked.connect(lambda: open_url(getattr(item,"link",""))); row.addWidget(open_btn)
        wa = QPushButton("◉  WhatsApp"); wa.setObjectName("newsWhatsApp"); wa.clicked.connect(lambda: open_whatsapp(getattr(item,"title",""),getattr(item,"link",""))); row.addWidget(wa)
        cp = QPushButton("▣  Copiar link"); cp.setObjectName("newsAction"); cp.clicked.connect(lambda: copy_text(getattr(item,"link",""))); row.addWidget(cp)
        extract = QPushButton("⇩  Extrair matéria"); extract.setObjectName("newsExtract"); extract.setEnabled(False); extract.setToolTip("Integração com o Extrator de Notícias será ligada em uma etapa separada, sem alterar o motor atual."); row.addWidget(extract)


def _set_period_checked(page, selected: QPushButton) -> None:
    for button in page._period_buttons:
        button.setChecked(button is selected)


def _run_period(page, button: QPushButton, hours: int | None) -> None:
    _set_period_checked(page, button)
    period = page.controller.period_today() if hours is None else page.controller.period_last_hours(hours)
    page.controller.search_news(*period)


def _page_changed(page, delta: int) -> None:
    page._page = max(0, min(page._page_count - 1, page._page + delta))
    page._render_cards(page.controller.state)


def _sort_changed(page) -> None:
    page._page = 0
    page._render_cards(page.controller.state)


def _news_init(self, controller) -> None:
    BasePage.__init__(self, controller)
    self.setObjectName("newsReferencePage")
    self.setStyleSheet(NEWS_STYLE)
    self._page = 0
    self._page_count = 1
    self._page_size = 5
    self._signature = None
    self._period_buttons = []

    self.root.setSpacing(9)
    self.root.addWidget(_NewsHero())

    filters = QFrame(); filters.setObjectName("newsFilter")
    fl = QVBoxLayout(filters); fl.setContentsMargins(14,10,14,10); fl.setSpacing(8)
    first = QHBoxLayout(); first.setSpacing(10)
    self.query = QLineEdit(); self.query.setObjectName("newsSearch"); self.query.setPlaceholderText("⌕   Buscar nas notícias (título, fonte, termo...)")
    self.search24 = QPushButton("⟳   Buscar últimas 24h"); self.search24.setObjectName("newsPrimary"); self.search24.clicked.connect(lambda: controller.search_news(*controller.period_last_hours(24)))
    self.only_demands = QCheckBox("Só demandas")
    first.addWidget(self.query,1); first.addWidget(self.search24); first.addWidget(self.only_demands)
    fl.addLayout(first)
    periods = QHBoxLayout(); periods.setSpacing(9)
    for label, hours in (("Hoje",None),("24 horas",24),("7 dias",168),("30 dias",720)):
        b = QPushButton(label); b.setObjectName("newsPeriod"); b.setCheckable(True); b.clicked.connect(lambda _=False,bb=b,h=hours:_run_period(self,bb,h)); periods.addWidget(b); self._period_buttons.append(b)
    self._period_buttons[0].setChecked(True)
    self.custom = QPushButton("▣   Período personalizado"); self.custom.setObjectName("newsPeriod"); self.custom.setCheckable(True); periods.addWidget(self.custom); periods.addStretch(); fl.addLayout(periods)
    self.period_box = QFrame(); pf = QHBoxLayout(self.period_box); pf.setContentsMargins(0,3,0,0)
    today=QDate.currentDate(); self.start_date=QDateEdit(today.addDays(-1)); self.start_time=QTimeEdit(QTime(0,0)); self.end_date=QDateEdit(today); self.end_time=QTimeEdit(QTime(23,59)); self.period_go=QPushButton("Buscar período"); self.period_go.setObjectName("newsPrimary")
    for w in (self.start_date,self.start_time,self.end_date,self.end_time,self.period_go): pf.addWidget(w)
    self.period_box.hide(); self.custom.toggled.connect(self.period_box.setVisible); self.period_go.clicked.connect(self._period); fl.addWidget(self.period_box)
    self.root.addWidget(filters)

    status_row = QHBoxLayout(); status_row.setSpacing(10)
    self.exec_box = QFrame(); self.exec_box.setObjectName("newsExec")
    eb = QVBoxLayout(self.exec_box); eb.setContentsMargins(14,10,14,10); eb.setSpacing(6)
    title_row = QHBoxLayout(); self.exec_icon=QLabel("✓"); self.exec_icon.setFixedSize(42,42); self.exec_icon.setAlignment(Qt.AlignmentFlag.AlignCenter); self.exec_icon.setStyleSheet("color:#1ce0a2;background:#084d45;border:1px solid #12aa82;border-radius:21px;font-size:24px;font-weight:900;"); title_row.addWidget(self.exec_icon)
    tx=QVBoxLayout(); tx.setSpacing(0); self.exec_title=QLabel("Busca concluída com sucesso"); self.exec_title.setObjectName("newsSectionTitle"); self.exec_sub=QLabel(); self.exec_sub.setObjectName("newsMuted"); tx.addWidget(self.exec_title); tx.addWidget(self.exec_sub); title_row.addLayout(tx,1); self.exec_pct=QLabel("100%"); self.exec_pct.setStyleSheet("color:#20e3aa;font-size:18px;font-weight:900;"); title_row.addWidget(self.exec_pct); eb.addLayout(title_row)
    self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setTextVisible(False); eb.addWidget(self.progress)
    self.exec_detail=QLabel(); self.exec_detail.setStyleSheet("color:#26e6ad;background:#073b40;border:1px solid #0a8f74;border-radius:7px;padding:6px 10px;"); eb.addWidget(self.exec_detail)
    status_row.addWidget(self.exec_box,3)

    self.metrics_box=QFrame(); self.metrics_box.setObjectName("newsMetrics"); mr=QHBoxLayout(self.metrics_box); mr.setContentsMargins(8,10,8,10); mr.setSpacing(0)
    self.metrics={}
    for key,icon,caption,color in (("pct","◉","Conclusão","#27e0d0"),("found","▤","Encontradas","#ffd150"),("fresh","✦","Novas","#bd61ff"),("errors","!","Falhas","#ff315a"),("steps","≋","Etapas","#23c6ff"),("time","◷","Tempo","#2be4ff")):
        m=_Metric(icon,caption,color); mr.addWidget(m,1); self.metrics[key]=m.value
    status_row.addWidget(self.metrics_box,2)
    self.root.addLayout(status_row)

    self.stop=QPushButton("■  Parar busca"); self.stop.setObjectName("newsAction"); self.stop.clicked.connect(controller.stop_news_search); self.stop.hide(); self.root.addWidget(self.stop,0,Qt.AlignmentFlag.AlignLeft)

    header=QHBoxLayout(); title=QLabel("▤  Notícias encontradas"); title.setObjectName("newsSectionTitle"); self.count=QLabel(); self.count.setObjectName("newsMuted"); header.addWidget(title); header.addWidget(self.count); header.addStretch()
    self.sort=QComboBox(); self.sort.addItems(["Mais recentes","Mais antigas"]); self.sort.currentIndexChanged.connect(lambda _:_sort_changed(self)); header.addWidget(self.sort)
    self.prev=QPushButton("‹"); self.prev.setObjectName("newsPager"); self.prev.clicked.connect(lambda:_page_changed(self,-1)); header.addWidget(self.prev)
    self.page_label=QLabel("1 de 1"); self.page_label.setObjectName("newsMuted"); header.addWidget(self.page_label)
    self.next=QPushButton("›"); self.next.setObjectName("newsPager"); self.next.clicked.connect(lambda:_page_changed(self,1)); header.addWidget(self.next)
    self.root.addLayout(header)

    self.scroll=QScrollArea(); self.scroll.setObjectName("newsScroll"); self.scroll.setWidgetResizable(True); self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.card_host=QWidget(); self.card_layout=QVBoxLayout(self.card_host); self.card_layout.setContentsMargins(0,0,0,0); self.card_layout.setSpacing(7); self.card_layout.addStretch(); self.scroll.setWidget(self.card_host); self.root.addWidget(self.scroll,1)

    self.query.textChanged.connect(lambda _: self._filter_changed(controller.state)); self.only_demands.toggled.connect(lambda _: self._filter_changed(controller.state))


def _news_period(self) -> None:
    p=self.controller.parse_period(self.start_date.date().toString("yyyy-MM-dd"),self.start_time.time().toString("HH:mm"),self.end_date.date().toString("yyyy-MM-dd"),self.end_time.time().toString("HH:mm"))
    if p: self.controller.search_news(*p)


def _news_rows(self,state):
    q=self.query.text().strip().lower()
    rows=[n for n in state.news if (not self.only_demands.isChecked() or bool(getattr(n,"demand",False))) and (not q or q in f"{getattr(n,'title','')} {getattr(n,'source','')} {getattr(n,'matchedTerm','')} {getattr(n,'matchedDemand','')}".lower())]
    rows.sort(key=lambda n:getattr(n,"date",0) or 0, reverse=self.sort.currentIndex()==0)
    return rows


def _filter_changed(self,state):
    self._page=0
    self._signature=None
    self.refresh(state)


def _clear_layout(layout) -> None:
    while layout.count():
        item=layout.takeAt(0); widget=item.widget()
        if widget is not None: widget.deleteLater()


def _render_cards(self,state) -> None:
    rows=self._rows(state)
    self._page_count=max(1,math.ceil(len(rows)/self._page_size))
    self._page=min(self._page,self._page_count-1)
    start=self._page*self._page_size; shown=rows[start:start+self._page_size]
    _clear_layout(self.card_layout)
    if shown:
        for idx,item in enumerate(shown,start=start): self.card_layout.addWidget(_ReferenceNewsCard(item,idx))
        self.card_layout.addStretch()
    else:
        empty=QLabel("Nenhuma notícia encontrada nesta visualização."); empty.setAlignment(Qt.AlignmentFlag.AlignCenter); empty.setObjectName("newsMuted"); self.card_layout.addStretch(); self.card_layout.addWidget(empty); self.card_layout.addStretch()
    self.count.setText(f"{len(rows)} resultado(s) para o período selecionado")
    self.page_label.setText(f"{self._page+1} de {self._page_count}")
    self.prev.setEnabled(self._page>0); self.next.setEnabled(self._page+1<self._page_count)


def _news_refresh(self,state) -> None:
    self.search24.setEnabled(not state.news_busy and self.controller.search_available)
    self.period_go.setEnabled(not state.news_busy and self.controller.search_available)
    self.stop.setVisible(state.news_busy)
    progress=state.news_progress
    fraction=max(0.0,min(1.0,float(getattr(progress,"fraction",0.0)))) if state.news_busy else 1.0
    pct=round(fraction*100); found=getattr(progress,"found",0); errors=getattr(progress,"errors",0); completed=getattr(progress,"completed",0); total=getattr(progress,"total",0); fresh=len(state.new_news_links)
    self.progress.setValue(pct); self.exec_pct.setText(f"{pct}%")
    self.metrics["pct"].setText(f"{pct}%"); self.metrics["found"].setText(str(found)); self.metrics["fresh"].setText(str(fresh)); self.metrics["errors"].setText(str(errors)); self.metrics["steps"].setText(f"{completed}/{total}"); self.metrics["time"].setText(duration(state.last_news_duration_ms))
    if state.news_busy:
        self.exec_title.setText("Busca de notícias em andamento"); self.exec_icon.setText("…"); self.exec_sub.setText(state.status or "Buscando..."); source=getattr(progress,"currentSource","") or "Preparando"; query=getattr(progress,"currentQuery","") or "consulta"; self.exec_detail.setText(f"{source} • {query}")
    else:
        self.exec_title.setText("Busca concluída com sucesso" if errors==0 else "Busca concluída com alertas"); self.exec_icon.setText("✓" if errors==0 else "!"); self.exec_sub.setText(f"0 demanda(s)  •  {found} resultado(s)  •  {fresh} novo(s)"); self.exec_detail.setText(f"A busca foi concluída. {found} notícia(s) encontrada(s) nesta execução.")
    signature=(self.query.text(),self.only_demands.isChecked(),self.sort.currentIndex(),self._page,tuple((getattr(n,"id",0),getattr(n,"link",""),getattr(n,"title",""),getattr(n,"date",0),getattr(n,"matchedTerm",""),getattr(n,"matchedDemand","")) for n in self._rows(state)))
    if signature!=self._signature:
        self._signature=signature; self._render_cards(state)


def install_v019_news_reference() -> None:
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED=True
    from monitor_noticias.ui.refined_search import NewsPage
    NewsPage.__init__=_news_init
    NewsPage._period=_news_period
    NewsPage._rows=_news_rows
    NewsPage._filter_changed=_filter_changed
    NewsPage._render_cards=_render_cards
    NewsPage.refresh=_news_refresh
