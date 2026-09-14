from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout

from monitor_noticias.ui.controller import MainUiController
from monitor_noticias.ui.refined_base import BasePage, card, dangerous, format_time, secondary
from monitor_noticias.ui.refined_cards import CardList, NewsCard, VideoCard


class DemandCard(QFrame):
    def __init__(self, demand, controller: MainUiController) -> None:
        super().__init__(); self.setObjectName("resultCard")
        row=QHBoxLayout(self); row.setContentsMargins(18,12,18,12); row.setSpacing(14)
        icon=QLabel("▣"); icon.setFixedSize(50,50); icon.setAlignment(Qt.AlignmentFlag.AlignCenter); icon.setStyleSheet("color:#ffc21a;background:#4c3e13;border:1px solid #a67d00;border-radius:9px;font-size:24px;"); row.addWidget(icon)
        text=QVBoxLayout(); text.setSpacing(3); title=QLabel(f"{demand.vehicle} • {demand.subject}"); title.setObjectName("smallTitle"); text.addWidget(title); meta=QLabel(f"Última busca: {format_time(demand.lastCheckedAt)}  •  encontrados {demand.lastFoundCount}  •  novos {demand.lastNewCount}"); meta.setObjectName("smallText"); text.addWidget(meta); row.addLayout(text,1)
        find=secondary(QPushButton("⌕  Buscar")); find.clicked.connect(lambda:controller.search_demand(demand)); delete=dangerous(QPushButton("▣")); delete.clicked.connect(lambda:controller.remove_demand(demand.id)); row.addWidget(find); row.addWidget(delete)


class DemandsPage(BasePage):
    def __init__(self,controller):
        super().__init__(controller); self._signature=None
        form,fl=card("filterCard",(16,14,16,14),8); labels=QHBoxLayout(); lv=QLabel("Veículo"); lv.setObjectName("smallTitle"); la=QLabel("Assunto"); la.setObjectName("smallTitle"); labels.addWidget(lv,1); labels.addWidget(la,2); labels.addSpacing(330); fl.addLayout(labels)
        row=QHBoxLayout(); row.setSpacing(12); self.vehicle=QLineEdit(); self.vehicle.setPlaceholderText("Selecione ou digite o veículo..."); self.subject=QLineEdit(); self.subject.setPlaceholderText("Digite o assunto da demanda..."); self.add=QPushButton("＋  Adicionar"); self.add.setProperty("gold",True); self.all=QPushButton("⟳  Buscar todas"); row.addWidget(self.vehicle,1); row.addWidget(self.subject,2); row.addWidget(self.add); row.addWidget(self.all); fl.addLayout(row); self.root.addWidget(form)
        status,_=card("statusCard",(20,15,20,15),4); sl=status.layout(); st=QHBoxLayout(); dot=QLabel("●"); dot.setStyleSheet("color:#17e59b;font-size:30px;"); st.addWidget(dot); sb=QVBoxLayout(); self.status_title=QLabel("Status: Pronto"); self.status_title.setObjectName("greenText"); self.status_detail=QLabel("Sistema disponível para consultar e gerenciar demandas."); self.status_detail.setObjectName("smallText"); sb.addWidget(self.status_title); sb.addWidget(self.status_detail); st.addLayout(sb,1); sl.addLayout(st); self.root.addWidget(status)
        self.list=CardList(); self.root.addWidget(self.list,1)
        self.add.clicked.connect(self._add); self.all.clicked.connect(controller.search_all_demands); self.vehicle.textChanged.connect(self._valid); self.subject.textChanged.connect(self._valid); self._valid()
    def _valid(self): self.add.setEnabled(bool(self.vehicle.text().strip() and self.subject.text().strip()))
    def _add(self): self.controller.add_demand(self.vehicle.text(),self.subject.text()); self.vehicle.clear(); self.subject.clear()
    def refresh(self,state):
        self.status_title.setText("Status: Buscando" if state.news_busy else "Status: Pronto"); self.status_detail.setText(state.status if state.news_busy else "Sistema disponível para consultar e gerenciar demandas."); self.all.setEnabled(not state.news_busy and self.controller.search_available)
        signature=tuple((d.id,d.vehicle,d.subject,d.lastCheckedAt,d.lastFoundCount,d.lastNewCount,d.active) for d in state.demands)
        if signature!=self._signature:
            self._signature=signature; self.list.set_cards([DemandCard(d,self.controller) for d in state.demands],[108]*len(state.demands))


class HistoryPage(BasePage):
    def __init__(self,controller):
        super().__init__(controller); self._signature=None; self._mode="news"
        bar,bl=card("filterCard",(12,10,12,10),4); row=QHBoxLayout(); self.news_tab=QPushButton("Notícias"); self.news_tab.setCheckable(True); self.news_tab.setChecked(True); self.video_tab=secondary(QPushButton("Vídeos")); self.video_tab.setCheckable(True); self.clear=dangerous(QPushButton("▣  Limpar histórico")); row.addWidget(self.news_tab); row.addWidget(self.video_tab); row.addStretch(); row.addWidget(self.clear); bl.addLayout(row); self.root.addWidget(bar)
        self.list=CardList(); self.root.addWidget(self.list,1)
        self.news_tab.clicked.connect(lambda:self._set_mode("news")); self.video_tab.clicked.connect(lambda:self._set_mode("video")); self.clear.clicked.connect(self._clear)
    def _set_mode(self,mode): self._mode=mode; self.news_tab.setChecked(mode=="news"); self.video_tab.setChecked(mode=="video"); self._signature=None; self.refresh(self.controller.state)
    def _clear(self): self.controller.clear_news_history() if self._mode=="news" else self.controller.clear_video_history(); self._signature=None; self.refresh(self.controller.state)
    def refresh(self,state):
        items=self.controller.news_db.listNews(2000) if self._mode=="news" else self.controller.video_db.listAll(2000)
        if self._mode=="news":
            signature=("n",tuple((n.id,n.link,n.title,n.date,n.matchedTerm,n.matchedDemand) for n in items))
        else:
            signature=("v",tuple((v.id,v.link,v.title,v.publishedAt,v.matchedTerm,v.matchedDemand) for v in items))
        if signature!=self._signature:
            self._signature=signature
            if self._mode=="news":
                cards=[NewsCard(n, actions_enabled=False) for n in items]
                heights=[128 if getattr(n,"snippet","") else 110 for n in items]
            else:
                cards=[VideoCard(v, actions_enabled=False) for v in items]
                heights=[106]*len(items)
            self.list.set_cards(cards,heights)


class TermColumn(QFrame):
    def __init__(self, title: str, subtitle: str, purple: bool, add_cb, remove_cb) -> None:
        super().__init__(); self.setObjectName("techCard"); self.add_cb=add_cb; self.remove_cb=remove_cb
        root=QVBoxLayout(self); root.setContentsMargins(18,16,18,16); root.setSpacing(10)
        head=QHBoxLayout(); icon=QLabel("▶" if purple else "▤"); icon.setFixedSize(54,54); icon.setAlignment(Qt.AlignmentFlag.AlignCenter); icon.setStyleSheet(("color:#c170ff;background:#352466;border:1px solid #7242a8;" if purple else "color:#5bd4ff;background:#075b8e;border:1px solid #0a86b8;")+"border-radius:10px;font-size:23px;"); head.addWidget(icon); hb=QVBoxLayout(); t=QLabel(title); t.setObjectName("sectionTitle"); sub=QLabel(subtitle); sub.setObjectName("smallText"); hb.addWidget(t); hb.addWidget(sub); head.addLayout(hb,1); self.counter=QLabel("0 termo(s)"); self.counter.setStyleSheet("color:#d8ebfa;background:#075284;border:1px solid #0b6c9c;border-radius:8px;padding:8px 12px;font-weight:800;"); head.addWidget(self.counter); root.addLayout(head)
        addrow=QHBoxLayout(); self.edit=QLineEdit(); self.edit.setPlaceholderText("⌕   Novo termo"); button=secondary(QPushButton("＋  Adicionar")); addrow.addWidget(self.edit,1); addrow.addWidget(button); root.addLayout(addrow)
        self.list=QListWidget(); root.addWidget(self.list,1); delete=dangerous(QPushButton("▣  Excluir selecionado")); root.addWidget(delete,0,Qt.AlignmentFlag.AlignRight)
        button.clicked.connect(self._add); delete.clicked.connect(self._delete)
    def _add(self):
        value=self.edit.text(); self.add_cb(value); self.edit.clear()
    def _delete(self):
        item=self.list.currentItem()
        if item: self.remove_cb(item.text())
    def set_values(self,values:Iterable[str]):
        vals=list(values); self.list.clear(); self.list.addItems(vals); self.counter.setText(f"{len(vals)} termo(s)")


class TermsPage(BasePage):
    def __init__(self,controller):
        super().__init__(controller); row=QHBoxLayout(); row.setSpacing(14); self.root.addLayout(row,1)
        self.news_col=TermColumn("Termos de Notícias","Usados na varredura de matérias",False,controller.add_term,controller.remove_term)
        self.video_col=TermColumn("Termos de Vídeos","Lista independente para vídeos",True,getattr(controller,"add_video_term",lambda _v:None),getattr(controller,"remove_video_term",lambda _v:None))
        row.addWidget(self.news_col,1); row.addWidget(self.video_col,1)
    def refresh(self,state): self.news_col.set_values(state.terms); self.video_col.set_values(getattr(self.controller,"video_terms",[]))
