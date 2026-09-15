from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar, QScrollArea, QVBoxLayout, QWidget

from monitor_noticias.ui.controller import MainUiController, UiState

HOME_REFERENCE_STYLE = r"""
QWidget#referenceHome { background:#020f1d; color:#f4f7ff; font-family:'Segoe UI'; }
QWidget#referenceHomeBody { background:#020f1d; }
QScrollArea#referenceHomeScroll, QScrollArea#referenceHomeScroll QWidget#qt_scrollarea_viewport { background:#020f1d; border:0; }
QLabel { background:transparent; color:#f4f7ff; }
QLabel#heroTitle { color:#ffffff; font-size:29px; font-weight:800; }
QLabel#heroSubtitle { color:#b7cde0; font-size:11px; }
QLabel#heroRail { color:#5bcaff; font-size:11px; font-weight:700; letter-spacing:2px; }
QLabel#heroQuote { color:#f3f7ff; font-size:11px; font-style:italic; }
QFrame#homePanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #05233a,stop:.55 #041d31,stop:1 #031729); border:1px solid #0b6f99; border-radius:11px; }
QLabel#panelTitle { color:#ffffff; font-size:11px; font-weight:800; }
QLabel#panelLink { color:#32bfff; font-size:9px; }
QLabel#smallText { color:#a9bfd3; font-size:9px; }
QLabel#tinyText { color:#8fa9bf; font-size:8px; }
QLabel#metricCaption { color:#9fb6cb; font-size:8px; }
QLabel#activePill { color:#3df0b0; background:#063f3a; border:1px solid #087d69; border-radius:9px; padding:3px 8px; font-size:8px; font-weight:800; }
QProgressBar#sourceBar { background:#06243a; border:0; border-radius:3px; min-height:6px; max-height:6px; }
QProgressBar#sourceBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00d9ff,stop:1 #0097ff); border-radius:3px; }
QLabel#footerText { color:#91aac1; font-size:8px; }
QLabel#footerRight { color:#4fd0ff; font-size:8px; font-weight:700; letter-spacing:1px; }
"""

def _label(text="", name=""):
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    return w

class ReferenceHero(QFrame):
    def __init__(self):
        super().__init__(); self.setFixedHeight(152); self.setObjectName("referenceHero")
        lay=QHBoxLayout(self); lay.setContentsMargins(20,14,18,12); lay.setSpacing(10)
        left=QVBoxLayout(); left.setSpacing(3); left.addStretch(1)
        left.addWidget(_label("Olá! Bem-vindo ao\nMonitor de Notícias","heroTitle"))
        left.addWidget(_label("Acompanhe, analise e transforme informações em decisões.","heroSubtitle")); left.addStretch(1)
        lay.addLayout(left,46); lay.addStretch(18)
        rail=_label("INFORMAÇÃO\nHOJE.\nDECISÕES\nAMANHÃ.","heroRail"); rail.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft); lay.addWidget(rail,16)
        quote_box=QVBoxLayout(); quote_box.setContentsMargins(10,8,4,8); quote_box.addWidget(_label("❞","heroRail"))
        quote=_label("Mais que monitoramento.\nInteligência para o seu tempo.","heroQuote"); quote.setWordWrap(True); quote_box.addWidget(quote); quote_box.addStretch(); lay.addLayout(quote_box,20)
    def paintEvent(self,event):
        super().paintEvent(event); p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        r=self.rect().adjusted(1,1,-1,-1); grad=QLinearGradient(r.left(),r.top(),r.right(),r.bottom()); grad.setColorAt(0,QColor("#03172a")); grad.setColorAt(.48,QColor("#073558")); grad.setColorAt(1,QColor("#031627"))
        p.setPen(QPen(QColor("#0a638d"),1)); p.setBrush(grad); p.drawRoundedRect(QRectF(r),11,11)
        cx,cy=self.width()*.49,self.height()*.54; radius=self.height()*.62
        glow=QLinearGradient(cx-radius,cy-radius,cx+radius,cy+radius); glow.setColorAt(0,QColor(0,40,80,0)); glow.setColorAt(.52,QColor(0,132,255,100)); glow.setColorAt(1,QColor(0,40,80,0)); p.setPen(Qt.PenStyle.NoPen); p.setBrush(glow); p.drawEllipse(QPointF(cx,cy),radius,radius)
        p.setBrush(QColor(3,29,58,205)); p.setPen(QPen(QColor(0,174,255,180),1.1)); p.drawEllipse(QPointF(cx,cy),radius*.78,radius*.78); p.setBrush(Qt.BrushStyle.NoBrush)
        for rr,a in ((.72,115),(.55,92),(.38,75)):
            p.setPen(QPen(QColor(0,193,255,a),1)); p.drawEllipse(QPointF(cx,cy),radius*rr,radius*rr*.54)
        p.setPen(QPen(QColor(24,190,255,140),1)); nodes=[(-.46,-.20,-.18,-.46),(-.18,-.46,.12,-.22),(.12,-.22,.34,.05),(-.35,.10,-.06,.27),(-.06,.27,.18,.15),(.18,.15,.42,.34),(-.24,.42,.08,.48),(.08,.48,.32,.30)]
        for x1,y1,x2,y2 in nodes:
            a=QPointF(cx+radius*x1,cy+radius*y1); b=QPointF(cx+radius*x2,cy+radius*y2); p.drawLine(a,b); p.setBrush(QColor("#00c9ff")); p.drawEllipse(b,2.1,2.1); p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(0,181,255,100),1))
        for i in range(8):
            x=self.width()*(.25+i*.075); p.drawLine(QPointF(x,0),QPointF(x+48,self.height()))
        p.setPen(QPen(QColor("#00d9ff"),2)); p.drawLine(QPointF(self.width()*.70,self.height()*.82),QPointF(self.width()*.77,self.height()*.82)); p.drawLine(QPointF(self.width()*.93,self.height()*.86),QPointF(self.width()*.955,self.height()*.86))

class ModuleCard(QFrame):
    clicked=Signal(str)
    def __init__(self,route,glyph,title,accent,subtitle):
        super().__init__(); self.route=route; self.setCursor(Qt.CursorShape.PointingHandCursor); self.setMinimumHeight(126); self.setMaximumHeight(132)
        self.setStyleSheet(f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #08253c,stop:.72 #071d34,stop:1 #0b1b34);border:1px solid {accent};border-radius:11px;}} QLabel{{border:0;background:transparent;}}")
        lay=QVBoxLayout(self); lay.setContentsMargins(12,10,10,9); lay.setSpacing(2)
        top=QHBoxLayout(); icon=QLabel(glyph); icon.setStyleSheet(f"color:{accent};font-size:23px;font-weight:800;border:0;"); top.addWidget(icon); top.addStretch(); arrow=QLabel("›"); arrow.setStyleSheet("color:#d7e8f8;font-size:20px;border:0;"); top.addWidget(arrow); lay.addLayout(top)
        name=QLabel(title); name.setStyleSheet("color:#ffffff;font-size:10px;font-weight:800;border:0;"); lay.addWidget(name)
        self.value=QLabel("—"); self.value.setStyleSheet("color:#ffffff;font-size:16px;font-weight:800;border:0;"); lay.addWidget(self.value)
        self.sub=QLabel(subtitle); self.sub.setStyleSheet("color:#8facbf;font-size:8px;border:0;"); lay.addWidget(self.sub)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton: self.clicked.emit(self.route)
        super().mousePressEvent(event)

class HourlyChart(QWidget):
    def __init__(self):
        super().__init__(); self.news=[0]*24; self.videos=[0]*24; self.demands=[0]*24; self.setMinimumHeight(112)
    def set_values(self,news,videos,demands): self.news,self.videos,self.demands=list(news),list(videos),list(demands); self.update()
    def paintEvent(self,event):
        super().paintEvent(event); p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing,True); r=self.rect().adjusted(30,8,-8,-22); maximum=max([1]+self.news+self.videos+self.demands)
        p.setPen(QPen(QColor(91,145,177,55),1))
        for i in range(5):
            y=r.bottom()-r.height()*i/4; p.drawLine(QPointF(r.left(),y),QPointF(r.right(),y))
        group_w=r.width()/24.0; bw=max(1.5,group_w*.18); colors=(QColor("#00c9ff"),QColor("#9256ff"),QColor("#ffc21a")); datasets=(self.news,self.videos,self.demands)
        for hour in range(24):
            x0=r.left()+hour*group_w+group_w*.18
            for j,data in enumerate(datasets):
                h=r.height()*(data[hour]/maximum); p.setPen(Qt.PenStyle.NoPen); p.setBrush(colors[j]); p.drawRoundedRect(QRectF(x0+j*bw*1.25,r.bottom()-h,bw,h),1.5,1.5)
        p.setPen(QPen(QColor("#91aac0"),1))
        for hour in range(0,24,2):
            x=r.left()+hour*group_w; p.drawText(QRectF(x-9,r.bottom()+4,24,14),Qt.AlignmentFlag.AlignCenter,f"{hour:02d}h")

class ReferenceHome(QWidget):
    navigate=Signal(str)
    CARD_SPECS=(("NEWS","▤","Notícias","#00c9ff","encontradas hoje"),("VIDEOS","▷","Vídeos","#9256ff","capturados hoje"),("DEMANDS","✉","Demandas","#ffc21a","ativas"),("SOURCES","◉","Fontes","#00c9ff","cadastradas"),("TERMS","⌕","Termos","#9b55ff","monitorados"),("COVERS","▧","Capas","#14bfff","jornais"),("PDF_EDITOR","▱","Editor de PDF","#00c9ff","ferramenta"),("EXTRACTOR","▦","Extrator de Vídeos","#a25cff","ferramenta"),("VIDEO_EDITOR","✂","Editor de Vídeo","#ef42b9","ferramenta"))
    def __init__(self,controller:MainUiController):
        super().__init__(); self.controller=controller; self.setObjectName("referenceHome"); self.setStyleSheet(HOME_REFERENCE_STYLE)
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0); scroll=QScrollArea(); scroll.setObjectName("referenceHomeScroll"); scroll.setWidgetResizable(True); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body=QWidget(); body.setObjectName("referenceHomeBody"); self.body=QVBoxLayout(body); self.body.setContentsMargins(12,8,12,6); self.body.setSpacing(10); scroll.setWidget(body); root.addWidget(scroll)
        self.body.addWidget(ReferenceHero()); self._build_module_cards(); self._build_middle(); self._build_bottom(); self._build_footer()
    def _panel(self,title,link=None):
        frame=QFrame(); frame.setObjectName("homePanel"); lay=QVBoxLayout(frame); lay.setContentsMargins(12,10,12,10); lay.setSpacing(6); head=QHBoxLayout(); head.addWidget(_label(title,"panelTitle")); head.addStretch()
        if link: head.addWidget(_label(link,"panelLink"))
        lay.addLayout(head); return frame,lay
    def _build_module_cards(self):
        row=QHBoxLayout(); row.setSpacing(8); self.module_cards={}
        for route,glyph,title,accent,subtitle in self.CARD_SPECS:
            card=ModuleCard(route,glyph,title,accent,subtitle); card.clicked.connect(self.navigate.emit); self.module_cards[route]=card; row.addWidget(card,1)
        self.body.addLayout(row)
    def _build_middle(self):
        grid=QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(0)
        monitor,ml=self._panel("✧  Monitoramento em tempo real"); top=QHBoxLayout(); self.monitor_toggle=_label("●  SISTEMA ATIVO","activePill"); top.addWidget(_label("  ◉   ◉","smallText")); top.addStretch(); top.addWidget(self.monitor_toggle); ml.addLayout(top); line=QFrame(); line.setFixedHeight(1); line.setStyleSheet("background:#0b5477;border:0;"); ml.addWidget(line); metrics=QHBoxLayout(); self.live_values={}
        for key,caption,color in (("pct","Conclusão","#00e2c1"),("found","Encontrados","#00d9ff"),("new","Novos","#ff355d"),("fails","Falhas","#8d5cff"),("steps","Etapas","#19b8ff"),("time","Tempo","#00d9ff")):
            col=QVBoxLayout(); value=QLabel("0"); value.setStyleSheet(f"color:{color};font-size:14px;font-weight:800;"); cap=_label(caption,"metricCaption"); value.setAlignment(Qt.AlignmentFlag.AlignCenter); cap.setAlignment(Qt.AlignmentFlag.AlignCenter); col.addWidget(value); col.addWidget(cap); metrics.addLayout(col,1); self.live_values[key]=value
        ml.addLayout(metrics); grid.addWidget(monitor,0,0)
        sources,sl=self._panel("▤  Fontes mais ativas hoje"); self.source_rows=[]
        for _ in range(5):
            rr=QHBoxLayout(); name=_label("—","smallText"); bar=QProgressBar(); bar.setObjectName("sourceBar"); bar.setRange(0,100); bar.setTextVisible(False); count=_label("0","smallText"); rr.addWidget(name,42); rr.addWidget(bar,45); rr.addWidget(count,8); sl.addLayout(rr); self.source_rows.append((name,bar,count))
        grid.addWidget(sources,0,1)
        auto,al=self._panel("◷  Automação e agendamentos","Ver tudo →"); self.auto_rows={}
        for key,glyph,title in (("news","▣","Notícias"),("demands","✉","Demandas"),("videos","▷","Vídeos")):
            ar=QHBoxLayout(); icon=QLabel(glyph); icon.setStyleSheet("color:#53cfff;font-size:16px;"); text=QVBoxLayout(); text.setSpacing(0); text.addWidget(_label(title,"smallText")); detail=_label("—","tinyText"); text.addWidget(detail); active=_label("Ativo","activePill"); ar.addWidget(icon); ar.addLayout(text,1); ar.addWidget(active); al.addLayout(ar); self.auto_rows[key]=(detail,active)
        grid.addWidget(auto,0,2)
        tips,tl=self._panel("💡  Dicas do sistema","1/3   ‹   ›"); tip=QFrame(); tip.setStyleSheet("background:#06253d;border:1px solid #0a6d96;border-radius:9px;"); tip_l=QVBoxLayout(tip); tip_l.setContentsMargins(12,10,12,10); tip_l.addWidget(_label("🚀   Use termos específicos","panelTitle")); desc=_label("Termos bem definidos trazem\nresultados mais relevantes.","smallText"); desc.setWordWrap(True); tip_l.addWidget(desc); tl.addWidget(tip,1); dots=_label("●  ●  ●","panelLink"); dots.setAlignment(Qt.AlignmentFlag.AlignCenter); tl.addWidget(dots); grid.addWidget(tips,0,3)
        grid.setColumnStretch(0,31); grid.setColumnStretch(1,23); grid.setColumnStretch(2,25); grid.setColumnStretch(3,21); self.body.addLayout(grid)
    def _build_bottom(self):
        row=QHBoxLayout(); row.setSpacing(10); activity,acl=self._panel("〽  Atividade recente","Ver histórico →"); self.activity_labels=[]; colors=["#00d9ff","#8d5cff","#00c9ff","#00d89c","#00bfff"]
        for i in range(5):
            r=QHBoxLayout(); t=_label("--:--","smallText"); dot=QLabel("●"); dot.setStyleSheet(f"color:{colors[i]};font-size:13px;"); text=_label("","smallText"); text.setWordWrap(True); r.addWidget(dot); r.addWidget(t); r.addWidget(text,1); acl.addLayout(r); self.activity_labels.append((t,text))
        row.addWidget(activity,40)
        chart_panel,cpl=self._panel("▥  Panorama das últimas 24 horas"); legend=QHBoxLayout(); legend.addStretch(); legend.addWidget(_label("■ Notícias","tinyText")); legend.addWidget(_label("■ Vídeos","tinyText")); legend.addWidget(_label("■ Demandas","tinyText")); legend.addWidget(_label("Últimas 24 horas","smallText")); cpl.addLayout(legend); self.chart=HourlyChart(); cpl.addWidget(self.chart,1); sums=QHBoxLayout(); self.summary={}
        for key,glyph,title,accent in (("news","▤","Total de notícias","#00c9ff"),("videos","▷","Total de vídeos","#9256ff"),("demands","✉","Demandas atendidas","#ffc21a")):
            box=QFrame(); box.setStyleSheet("background:#05233a;border:1px solid #0b648e;border-radius:9px;"); bl=QHBoxLayout(box); bl.setContentsMargins(10,7,10,7); icon=QLabel(glyph); icon.setStyleSheet(f"color:{accent};font-size:19px;font-weight:800;"); val=QLabel("0"); val.setStyleSheet("color:#fff;font-size:15px;font-weight:800;"); txt=QVBoxLayout(); txt.addWidget(val); txt.addWidget(_label(title,"tinyText")); bl.addWidget(icon); bl.addLayout(txt,1); sums.addWidget(box,1); self.summary[key]=val
        cpl.addLayout(sums); row.addWidget(chart_panel,60); self.body.addLayout(row)
    def _build_footer(self):
        footer=QFrame(); footer.setFixedHeight(24); footer.setStyleSheet("background:#020f1d;border-top:1px solid #0a456b;"); lay=QHBoxLayout(footer); lay.setContentsMargins(4,3,4,2); lay.addWidget(_label("Monitor de Notícias v4.0.2   |   Inteligência de mídia para melhores decisões","footerText")); lay.addStretch(); self.footer_status=_label("●  Sistema operacional","footerText"); self.footer_status.setStyleSheet("color:#49dfaa;font-size:8px;"); lay.addWidget(self.footer_status); lay.addWidget(_label("—","footerText")); lay.addWidget(_label("MAR • TERRA • AR • CIBERESPAÇO","footerRight")); self.body.addWidget(footer)
    @staticmethod
    def _published_ms(item,*names):
        for name in names:
            try: value=int(getattr(item,name,0) or 0)
            except (TypeError,ValueError): value=0
            if value: return value
        return 0
    @staticmethod
    def _progress_fraction(progress):
        try: return max(0.0,min(1.0,float(getattr(progress,"fraction",0.0))))
        except Exception: return 0.0
    def _hour_buckets(self,items,field_names):
        now=datetime.now(); start=now-timedelta(hours=24); out=[0]*24
        for item in items:
            ms=self._published_ms(item,*field_names)
            if not ms: continue
            dt=datetime.fromtimestamp(ms/1000)
            if start<=dt<=now:
                diff=int((dt-start).total_seconds()//3600); out[min(23,max(0,diff))]+=1
        return out
    def refresh(self,state:UiState):
        now=datetime.now(); cutoff=int((now-timedelta(hours=24)).timestamp()*1000); news_24=sum(1 for item in state.news if self._published_ms(item,"date")>=cutoff); videos_24=sum(1 for item in state.videos if self._published_ms(item,"capturedAt","date")>=cutoff); demands_active=sum(1 for item in state.demands if bool(getattr(item,"active",False)))
        values={"NEWS":news_24,"VIDEOS":videos_24,"DEMANDS":demands_active,"SOURCES":len(self.controller.news_sources),"TERMS":len(state.terms),"COVERS":"—","PDF_EDITOR":"—","EXTRACTOR":"—","VIDEO_EDITOR":"—"}
        for key,value in values.items(): self.module_cards[key].value.setText(str(value))
        busy=state.news_busy or state.video_busy; progress=state.news_progress if state.news_busy else state.video_progress; pct=round(self._progress_fraction(progress)*100) if busy else 100; self.live_values["pct"].setText(f"{pct}%"); self.live_values["found"].setText(str(len(state.news))); self.live_values["new"].setText(str(len(state.new_news_links))); fails=getattr(progress,"failed",getattr(progress,"failures",0)); self.live_values["fails"].setText(str(fails or 0)); current=getattr(progress,"current",getattr(progress,"completed",0)); total=getattr(progress,"total",0); self.live_values["steps"].setText(f"{current}/{total}" if total else "—"); duration_ms=state.last_news_duration_ms if not state.video_busy else state.last_video_duration_ms; seconds=max(0,int(duration_ms/1000)); self.live_values["time"].setText(f"{seconds//60:02d}:{seconds%60:02d}"); self.footer_status.setText("●  Busca em andamento" if busy else "●  Sistema operacional")
        ranking=Counter()
        for item in state.news:
            source=str(getattr(item,"source","") or "").strip()
            if source: ranking[source]+=1
        top=ranking.most_common(5); max_count=max([1]+[c for _,c in top])
        for idx,(name,bar,count) in enumerate(self.source_rows):
            if idx<len(top):
                source,value=top[idx]; name.setText(source); count.setText(str(value)); bar.setValue(round(value*100/max_count))
            else: name.setText("—"); count.setText(""); bar.setValue(0)
        auto=self.controller.automation_settings; self.monitor_toggle.setText("●  SISTEMA ATIVO" if auto.automatic_monitoring else "●  SISTEMA PAUSADO"); self.auto_rows["news"][0].setText(f"A cada {auto.news_interval_minutes} minutos"); self.auto_rows["demands"][0].setText(f"A cada {auto.demand_interval_minutes} minutos"); slots=sorted(auto.video_schedule_times); self.auto_rows["videos"][0].setText("Horários definidos" if slots else "Sem horários")
        for _,active in self.auto_rows.values(): active.setText("Ativo" if auto.automatic_monitoring else "Pausado")
        activity=[]
        if state.status: activity.append((now.strftime("%H:%M"),f"Notícias: {state.status}"))
        if state.video_status: activity.append((now.strftime("%H:%M"),f"Vídeos: {state.video_status}"))
        activity.extend([(now.strftime("%H:%M"),f"Fontes carregadas: {len(self.controller.news_sources)}"),(now.strftime("%H:%M"),f"Termos monitorados: {len(state.terms)}"),(now.strftime("%H:%M"),"Sistema operacional")])
        for idx,(time_label,text_label) in enumerate(self.activity_labels):
            if idx<len(activity): time_label.setText(activity[idx][0]); text_label.setText(activity[idx][1])
            else: time_label.setText(""); text_label.setText("")
        self.chart.set_values(self._hour_buckets(state.news,("date",)),self._hour_buckets(state.videos,("capturedAt","date")),[0]*24); self.summary["news"].setText(str(news_24)); self.summary["videos"].setText(str(videos_24)); self.summary["demands"].setText(str(demands_active))

_INSTALLED=False
def install_v017_home_truth():
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED=True
    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section, SECTION_ORDER
    old_build=MainWindow._build_ui
    def build(self):
        old_build(self); old=self.pages.get(Section.HOME); idx=SECTION_ORDER.index(Section.HOME); page=ReferenceHome(self.controller); page.navigate.connect(lambda name:self.navigate(Section[name])); self.stack.removeWidget(old)
        if old is not None: old.deleteLater()
        self.stack.insertWidget(idx,page); self.pages[Section.HOME]=page
        top=getattr(self,"reference_top_bar",None)
        if top is not None: top.search.setPlaceholderText("⌕   Buscar notícias, fontes, demandas... ou digite um comando (Ctrl + K)")
    MainWindow._build_ui=build
