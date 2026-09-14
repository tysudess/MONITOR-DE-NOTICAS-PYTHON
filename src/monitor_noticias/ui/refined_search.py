from __future__ import annotations

from PySide6.QtCore import QDate, Qt, QTime
from PySide6.QtWidgets import QCheckBox, QDateEdit, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTimeEdit, QVBoxLayout

from monitor_noticias.ui.controller import MainUiController
from monitor_noticias.ui.refined_base import BasePage, ExecutionPanel, card, dangerous, secondary
from monitor_noticias.ui.refined_cards import CardList, NewsCard, VideoCard


class NewsPage(BasePage):
    def __init__(self, controller: MainUiController) -> None:
        super().__init__(controller)
        self._signature = None
        top, tl = card("filterCard", (16, 12, 16, 12), 9)
        first = QHBoxLayout(); first.setSpacing(12)
        self.query = QLineEdit(); self.query.setPlaceholderText("⌕   Buscar nas notícias (título, fonte, termo...)")
        self.only_demands = QCheckBox("Só demandas")
        self.search24 = QPushButton("⟳  Buscar últimas 24h")
        self.search24.clicked.connect(lambda: controller.search_news(*controller.period_last_hours(24)))
        first.addWidget(self.query,1); first.addWidget(self.search24); first.addWidget(self.only_demands)
        tl.addLayout(first)
        periods=QHBoxLayout(); periods.setSpacing(9)
        for label,hours in (("Hoje",None),("24 horas",24),("7 dias",168),("30 dias",720)):
            b=secondary(QPushButton(label)); b.clicked.connect(lambda _=False,h=hours: controller.search_news(*(controller.period_today() if h is None else controller.period_last_hours(h))))
            periods.addWidget(b)
        self.custom=secondary(QPushButton("Período personalizado")); self.custom.setCheckable(True); periods.addWidget(self.custom); periods.addStretch(); tl.addLayout(periods)
        self.period_box=QFrame(); form=QHBoxLayout(self.period_box); form.setContentsMargins(0,4,0,0)
        today=QDate.currentDate(); self.start_date=QDateEdit(today.addDays(-1)); self.start_time=QTimeEdit(QTime(0,0)); self.end_date=QDateEdit(today); self.end_time=QTimeEdit(QTime(23,59)); self.period_go=QPushButton("Buscar período")
        for w in (self.start_date,self.start_time,self.end_date,self.end_time,self.period_go): form.addWidget(w)
        self.period_box.hide(); self.custom.toggled.connect(self.period_box.setVisible); self.period_go.clicked.connect(self._period); tl.addWidget(self.period_box)
        self.root.addWidget(top)
        self.exec=ExecutionPanel("Notícias"); self.root.addWidget(self.exec)
        self.stop=dangerous(QPushButton("■  Parar busca")); self.stop.clicked.connect(controller.stop_news_search); self.root.addWidget(self.stop,0,Qt.AlignmentFlag.AlignLeft)
        hr=QHBoxLayout(); title=QLabel("Notícias encontradas"); title.setObjectName("sectionTitle"); self.count=QLabel(); self.count.setObjectName("smallText"); hr.addWidget(title); hr.addStretch(); hr.addWidget(self.count); self.root.addLayout(hr)
        self.list=CardList(); self.root.addWidget(self.list,1)
        self.query.textChanged.connect(lambda _:self.refresh(controller.state)); self.only_demands.toggled.connect(lambda _:self.refresh(controller.state))

    def _period(self):
        p=self.controller.parse_period(self.start_date.date().toString("yyyy-MM-dd"),self.start_time.time().toString("HH:mm"),self.end_date.date().toString("yyyy-MM-dd"),self.end_time.time().toString("HH:mm"))
        if p: self.controller.search_news(*p)

    def _rows(self,state):
        q=self.query.text().strip().lower()
        return [n for n in state.news if (not self.only_demands.isChecked() or n.demand) and (not q or q in f"{n.title} {n.source} {n.matchedTerm} {n.matchedDemand}".lower())]

    def refresh(self,state):
        rows=self._rows(state); self.count.setText(f"{len(rows)} exibida(s)")
        self.search24.setEnabled(not state.news_busy and self.controller.search_available); self.period_go.setEnabled(not state.news_busy and self.controller.search_available); self.stop.setVisible(state.news_busy)
        self.exec.set_state(state.news_busy,state.news_progress,state.status,len(state.new_news_links),state.last_news_duration_ms)
        signature=(self.query.text(),self.only_demands.isChecked(),tuple((getattr(n,"id",0),n.link,n.title,n.date,n.matchedTerm,n.matchedDemand) for n in rows))
        if signature!=self._signature:
            self._signature=signature
            cards=[NewsCard(n) for n in rows]
            heights=[128 if getattr(n,"snippet","") else 110 for n in rows]
            self.list.set_cards(cards,heights)


class VideosPage(BasePage):
    def __init__(self,controller):
        super().__init__(controller); self._signature=None
        top,tl=card("filterCard",(16,12,16,12),9); row=QHBoxLayout(); row.setSpacing(12)
        self.query=QLineEdit(); self.query.setPlaceholderText("⌕   Buscar nos vídeos (título, fonte, termo...)"); row.addWidget(self.query,1)
        self.run=QPushButton("⟳  Buscar vídeos agora"); self.run.clicked.connect(controller.search_videos); row.addWidget(self.run); tl.addLayout(row)
        prow=QHBoxLayout(); prow.setSpacing(9)
        for label,h in (("24 horas",24),("7 dias",168),("30 dias",720)):
            b=secondary(QPushButton(label)); b.clicked.connect(lambda _=False,h=h: controller.search_videos(*controller.period_last_hours(h))); prow.addWidget(b)
        custom=secondary(QPushButton("Período personalizado")); custom.setEnabled(False); custom.setToolTip("O motor atual de vídeos não expõe período personalizado nesta tela."); prow.addWidget(custom); prow.addStretch(); tl.addLayout(prow); self.root.addWidget(top)
        self.exec=ExecutionPanel("Vídeos"); self.root.addWidget(self.exec)
        self.stop=dangerous(QPushButton("■  Parar busca")); self.stop.clicked.connect(controller.stop_video_search); self.root.addWidget(self.stop,0,Qt.AlignmentFlag.AlignLeft)
        self.warning=QLabel(); self.warning.setWordWrap(True); self.warning.setStyleSheet("color:#ffd34d;background:#3a3215;border:1px solid #9b7e0a;border-radius:7px;padding:6px 9px;"); self.warning.hide(); self.root.addWidget(self.warning)
        hr=QHBoxLayout(); title=QLabel("Vídeos encontrados"); title.setObjectName("sectionTitle"); self.count=QLabel(); self.count.setObjectName("smallText"); hr.addWidget(title); hr.addStretch(); hr.addWidget(self.count); self.root.addLayout(hr)
        self.list=CardList(); self.root.addWidget(self.list,1)
        self.empty=QFrame(); self.empty.setObjectName("emptyPanel"); el=QVBoxLayout(self.empty); el.addStretch(); play=QLabel("▶"); play.setAlignment(Qt.AlignmentFlag.AlignCenter); play.setStyleSheet("color:#b45cff;font-size:38px;"); el.addWidget(play); et=QLabel("Nenhum vídeo nesta visualização"); et.setAlignment(Qt.AlignmentFlag.AlignCenter); et.setObjectName("sectionTitle"); el.addWidget(et); es=QLabel("Execute uma busca manual ou selecione outras fontes de vídeo."); es.setAlignment(Qt.AlignmentFlag.AlignCenter); es.setObjectName("smallText"); el.addWidget(es); el.addStretch(); self.root.addWidget(self.empty,1)
        self.query.textChanged.connect(lambda _:self.refresh(controller.state))

    def refresh(self,state):
        q=self.query.text().strip().lower(); rows=[v for v in state.videos if not q or q in f"{v.title} {v.sourceName} {v.matchedTerm} {v.matchedDemand}".lower()]
        self.count.setText(f"{len(rows)} exibido(s)"); self.run.setEnabled(not state.video_busy and self.controller.search_available); self.stop.setVisible(state.video_busy); self.exec.set_state(state.video_busy,state.video_progress,state.video_status,len(state.new_video_links),state.last_video_duration_ms)
        if state.unstable_video_sources: self.warning.setText("Fontes com instabilidade: "+" • ".join(str(getattr(x,"sourceName",x)) for x in state.unstable_video_sources)); self.warning.show()
        else: self.warning.hide()
        self.list.setVisible(bool(rows)); self.empty.setVisible(not rows)
        signature=(self.query.text(),tuple((getattr(v,"id",0),v.link,v.title,v.publishedAt,v.matchedTerm,v.matchedDemand) for v in rows))
        if signature!=self._signature:
            self._signature=signature; self.list.set_cards([VideoCard(v) for v in rows],[106]*len(rows))
