from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from monitor_noticias.ui.catalog import REGIONS, STATES
from monitor_noticias.ui.refined_base import BasePage, ToggleSwitch, card, secondary


class SourceRow(QWidget):
    toggled = Signal(str, bool)
    def __init__(self, source, checked: bool, enabled: bool) -> None:
        super().__init__(); self.source=source
        row=QHBoxLayout(self); row.setContentsMargins(10,4,10,4); row.setSpacing(12)
        self.check=QCheckBox(); self.check.setChecked(checked); self.check.setEnabled(enabled); row.addWidget(self.check)
        initials="".join(part[:1] for part in source.name.split()[:3]).upper()[:3] or source.name[:3].upper(); sig=QLabel(initials); sig.setFixedSize(64,38); sig.setAlignment(Qt.AlignmentFlag.AlignCenter); sig.setStyleSheet("color:#ffffff;background:#087af7;border:1px solid #22c5ff;border-radius:8px;font-weight:800;"); row.addWidget(sig)
        text=QVBoxLayout(); name=QLabel(source.name); name.setObjectName("smallTitle"); meta=QLabel(f"{source.group} • {getattr(source,'region','Nacional')} • {getattr(source,'state','') or 'BR'}"); meta.setObjectName("smallText"); text.addWidget(name); text.addWidget(meta); row.addLayout(text,1)
        badge=QLabel("modo todos" if not enabled else "selecionada" if checked else "disponível"); badge.setStyleSheet("color:#19e5a1;border:1px solid #0bba82;border-radius:7px;padding:5px 10px;font-weight:700;"); row.addWidget(badge); arrow=QLabel("›"); arrow.setStyleSheet("color:#20aaff;font-size:28px;"); row.addWidget(arrow)
        self.check.toggled.connect(lambda v:self.toggled.emit(source.id,v))


class SourcesPage(BasePage):
    def __init__(self,controller):
        super().__init__(controller); self._guard=False; self._signature=None; self._tab=0
        top,tl=card("filterCard",(14,10,14,12),8)
        tabrow=QHBoxLayout(); self.tab_buttons=[]
        for idx,text in enumerate(("Notícias","Vídeos","Mídia especializada")):
            b=secondary(QPushButton(text)); b.setCheckable(True); b.setChecked(idx==0); b.clicked.connect(lambda _=False,i=idx:self._set_tab(i)); tabrow.addWidget(b); self.tab_buttons.append(b)
        tabrow.addStretch(); self.query=QLineEdit(); self.query.setPlaceholderText("⌕   Pesquisar fonte..."); self.query.setMaximumWidth(460); tabrow.addWidget(self.query); tl.addLayout(tabrow)
        rrow=QHBoxLayout(); rrow.addWidget(QLabel("Região")); self.region_buttons=[]
        for region in REGIONS:
            b=secondary(QPushButton(region)); b.setCheckable(True); b.setChecked(region=="Todas"); b.clicked.connect(lambda _=False,r=region:self._set_region(r)); rrow.addWidget(b); self.region_buttons.append((region,b))
        rrow.addStretch(); tl.addLayout(rrow)
        self.region="Todas"; self.state="Todos"; self._state_regions={code:reg for code,_name,reg in STATES}; srow=QHBoxLayout(); srow.addWidget(QLabel("Estado")); self.state_buttons=[]; allb=secondary(QPushButton("Todos")); allb.setCheckable(True); allb.setChecked(True); allb.clicked.connect(lambda:self._set_state("Todos")); srow.addWidget(allb); self.state_buttons.append(("Todos",allb))
        for code,name,reg in STATES:
            b=secondary(QPushButton(code)); b.setCheckable(True); b.clicked.connect(lambda _=False,c=code:self._set_state(c)); srow.addWidget(b); self.state_buttons.append((code,b))
        srow.addStretch(); tl.addLayout(srow); self._sync_state_buttons(); self.root.addWidget(top)
        allbox,_=card("statusCard",(16,10,16,10),4); al=allbox.layout(); ar=QHBoxLayout(); globe=QLabel("●"); globe.setStyleSheet("color:#13e39a;font-size:27px;"); ar.addWidget(globe); at=QVBoxLayout(); title=QLabel("TODOS OS VEÍCULOS — SEM EXCEÇÃO"); title.setObjectName("greenText"); sub=QLabel("Ligado: aceita qualquer veículo encontrado, inclusive fora do catálogo padrão."); sub.setObjectName("smallText"); at.addWidget(title); at.addWidget(sub); ar.addLayout(at,1); self.all_label=QLabel("LIGADO"); self.all_label.setObjectName("greenText"); ar.addWidget(self.all_label); self.all_news=ToggleSwitch(); ar.addWidget(self.all_news); al.addLayout(ar); self.root.addWidget(allbox)
        tools,_=card("filterCard",(14,8,14,8),4); tr=QHBoxLayout(); self.info=QLabel(); self.info.setObjectName("sectionTitle"); tr.addWidget(self.info); tr.addStretch(); self.select_visible=QPushButton("Selecionar visíveis"); self.clear_visible=secondary(QPushButton("Limpar visíveis")); self.select_all=secondary(QPushButton("Todas")); self.clear_all=secondary(QPushButton("Nenhuma")); [tr.addWidget(b) for b in (self.select_visible,self.clear_visible,self.select_all,self.clear_all)]; tools.layout().addLayout(tr); self.root.addWidget(tools)
        self.list=QListWidget(); self.list.setSpacing(3); self.root.addWidget(self.list,1)
        self.query.textChanged.connect(lambda _:self.refresh(controller.state)); self.all_news.toggled.connect(self._all_news_changed); self.select_visible.clicked.connect(lambda:self._set_visible(True)); self.clear_visible.clicked.connect(lambda:self._set_visible(False)); self.select_all.clicked.connect(lambda:self._set_all(True)); self.clear_all.clicked.connect(lambda:self._set_all(False))
    def _set_tab(self,i): self._tab=i; [b.setChecked(j==i) for j,b in enumerate(self.tab_buttons)]; self._signature=None; self.refresh(self.controller.state)
    def _set_region(self,r):
        self.region=r; [b.setChecked(name==r) for name,b in self.region_buttons]; self.state="Todos"; [b.setChecked(name=="Todos") for name,b in self.state_buttons]; self._sync_state_buttons(); self._signature=None; self.refresh(self.controller.state)
    def _sync_state_buttons(self):
        for name,button in self.state_buttons:
            visible = name == "Todos" or self.region in {"Todas", "Nacional"} or self._state_regions.get(name) == self.region
            button.setVisible(visible)
    def _set_state(self,s): self.state=s; [b.setChecked(name==s) for name,b in self.state_buttons]; self._signature=None; self.refresh(self.controller.state)
    def _all_news_changed(self,v):
        if self._guard:return
        self.controller.news_all_sources=v; self._signature=None; self.refresh(self.controller.state)
    def _base(self): return self.controller.news_sources if self._tab==0 else (self.controller.video_sources if self._tab==1 else self.controller.specialized_sources)
    def _selected_sources(self):
        q=self.query.text().strip().lower(); result=[]
        for source in self._base():
            src_region=getattr(source,"region","Nacional") or "Nacional"; src_state=getattr(source,"state","") or "BR"
            if self.region!="Todas" and src_region!=self.region: continue
            if self.state!="Todos" and src_state!=self.state: continue
            hay=f"{source.name} {src_region} {src_state} {source.group} {' '.join(source.aliases)}".lower()
            if q and q not in hay: continue
            result.append(source)
        return result
    def refresh(self,state):
        self._guard=True; self.all_news.setChecked(self.controller.news_all_sources if self._tab!=1 else False); self.all_news.setEnabled(self._tab!=1); self.all_label.setText("LIGADO" if self.controller.news_all_sources and self._tab!=1 else "DESLIGADO" if self._tab!=1 else "N/A"); self._guard=False
        visible=self._selected_sources(); self.info.setText(f"▤   {len(visible)} fonte(s) visível(is)" + ("   seletor ignorado" if self.controller.news_all_sources and self._tab!=1 else ""))
        selected=self.controller.selected_video_source_ids if self._tab==1 else self.controller.selected_news_source_ids; enabled=self._tab==1 or not self.controller.news_all_sources
        signature=(self._tab,self.region,self.state,self.query.text(),self.controller.news_all_sources,tuple(sorted(selected)),tuple(s.id for s in visible))
        if signature==self._signature:return
        self._signature=signature; self.list.clear()
        for source in visible:
            item=QListWidgetItem(); item.setSizeHint(QSize(0,66)); self.list.addItem(item); widget=SourceRow(source,(not enabled or source.id in selected),enabled); widget.toggled.connect(self._source_toggled); self.list.setItemWidget(item,widget)
    def _source_toggled(self,source_id,checked):
        if self._tab==1:self.controller.set_video_source(source_id,checked)
        else:self.controller.set_news_source(source_id,checked)
        self._signature=None
    def _set_visible(self,checked):
        for source in self._selected_sources():
            if self._tab==1:self.controller.set_video_source(source.id,checked)
            else:self.controller.set_news_source(source.id,checked)
        self._signature=None; self.refresh(self.controller.state)
    def _set_all(self,checked):
        base=self._base()
        if self._tab==1:self.controller.selected_video_source_ids={s.id for s in base} if checked else set()
        else:
            if self._tab==0 and checked:self.controller.news_all_sources=True
            elif self._tab==0 and not checked:self.controller.news_all_sources=False; self.controller.selected_news_source_ids=set()
            else:
                ids=self.controller.selected_news_source_ids; spec={s.id for s in base}; self.controller.selected_news_source_ids=(ids|spec) if checked else (ids-spec)
        self._signature=None; self.refresh(self.controller.state)
