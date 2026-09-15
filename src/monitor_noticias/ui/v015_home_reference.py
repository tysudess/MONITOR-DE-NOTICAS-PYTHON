from __future__ import annotations

from datetime import datetime
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget,QFrame,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QGridLayout,QProgressBar


class GlobeHero(QFrame):
    def paintEvent(self,event):
        super().paintEvent(event)
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        w,h=self.width(),self.height();cx=w*.47;cy=h*.51;r=h*.92
        grad=QLinearGradient(cx-r,cy-r,cx+r,cy+r);grad.setColorAt(0,QColor(0,60,104,10));grad.setColorAt(.45,QColor(0,102,170,40));grad.setColorAt(1,QColor(0,25,55,0))
        p.setPen(Qt.PenStyle.NoPen);p.setBrush(grad);p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        for rr,a in ((r*.82,100),(r*.62,80),(r*.42,70),(r*.22,60)):
            p.setPen(QPen(QColor(0,160,255,a),1));p.drawEllipse(QPointF(cx,cy),rr,rr*.56)
        p.setPen(QPen(QColor(0,135,220,75),1))
        for off in (-.45,-.22,0,.22,.45):p.drawArc(QRectF(cx-r*.72+off*r*.18,cy-r*.72,r*1.44,r*1.44),75*16,210*16)
        p.setPen(QPen(QColor(30,185,255,95),1))
        for x1,y1,x2,y2 in ((.36,.31,.52,.21),(.42,.60,.58,.45),(.51,.37,.62,.28),(.47,.72,.64,.60),(.60,.48,.70,.34)):
            p.drawLine(QPointF(w*x1,h*y1),QPointF(w*x2,h*y2));p.drawEllipse(QPointF(w*x2,h*y2),2.4,2.4)
        p.setPen(QPen(QColor(0,112,175,45),1));
        for i in range(10):p.drawLine(QPointF(w*.26+i*w*.045,0),QPointF(w*.41+i*w*.04,h))


class MiniChart(QWidget):
    def __init__(self):super().__init__();self.values=[5,9,8,11,18,24,31,27,20,26,34,28,17,14,19,16,13,12]
    def paintEvent(self,event):
        super().paintEvent(event);p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing,True);w,h=self.width(),self.height()
        p.setPen(QPen(QColor(38,101,135,120),1))
        for i in range(5):y=8+i*(h-24)/4;p.drawLine(QPointF(28,y),QPointF(w-8,y))
        n=len(self.values);bw=max(3,(w-50)/(n*2.3));m=max(self.values) or 1
        for i,v in enumerate(self.values):
            x=34+i*(w-55)/n;bh=(h-28)*v/m
            p.fillRect(QRectF(x,h-16-bh,bw,bh),QColor('#00c9f5'))
            p.fillRect(QRectF(x+bw+2,h-16-bh*.37,bw*.75,bh*.37),QColor('#8a45de'))
            p.fillRect(QRectF(x+bw*1.9+3,h-16-bh*.18,bw*.55,bh*.18),QColor('#f4a614'))


def lab(text,name=None):
    x=QLabel(text)
    if name:x.setObjectName(name)
    return x


def card(name='refCard'):
    f=QFrame();f.setObjectName(name);return f


STYLE=r"""
QWidget#refHome{background:#031625;color:#eef7ff;font-family:'Segoe UI';}
QFrame#refHero{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #041a2d,stop:.68 #052742,stop:1 #04192b);border:1px solid #0a5d86;border-radius:12px;}
QLabel#heroTitle{font-size:28px;font-weight:800;color:#fff;} QLabel#heroSub{font-size:11px;color:#c8d7e6;} QLabel#heroRail{font-size:11px;font-weight:700;color:#5bcaff;letter-spacing:2px;} QLabel#heroQuote{font-size:12px;font-style:italic;color:#f3f6fb;}
QFrame#metric{border:1px solid #0b6d9a;border-radius:11px;background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #082b45,stop:1 #061d34);} QFrame#metric[active='1']{border:1px solid #00c4ff;}
QLabel#metricTitle{font-size:10px;font-weight:700;color:#fff;} QLabel#metricValue{font-size:19px;font-weight:800;color:#fff;} QLabel#metricSub{font-size:9px;color:#aac1d7;}
QFrame#panel{border:1px solid #0b6d9a;border-radius:11px;background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #07263e,stop:1 #051c31);} QLabel#panelTitle{font-size:12px;font-weight:800;color:#fff;} QLabel#panelSub{font-size:9px;color:#a9c0d5;}
QPushButton#linkBtn{background:transparent;border:0;color:#41c9ff;font-size:9px;text-align:right;padding:0;}
QProgressBar#homeProg{background:#0a3448;border:0;border-radius:4px;max-height:8px;min-height:8px;} QProgressBar#homeProg::chunk{background:#14de98;border-radius:4px;}
"""


class ReferenceHomePage(QWidget):
    navigate=Signal(str)
    def __init__(self,controller):
        super().__init__();self.controller=controller;self.setObjectName('refHome');self.setStyleSheet(STYLE)
        root=QVBoxLayout(self);root.setContentsMargins(12,0,12,10);root.setSpacing(10)
        self.hero=GlobeHero();self.hero.setObjectName('refHero');self.hero.setFixedHeight(154);hl=QHBoxLayout(self.hero);hl.setContentsMargins(20,16,18,14);hl.setSpacing(16)
        left=QVBoxLayout();left.setSpacing(3);left.addWidget(lab('Olá! Bem-vindo ao\nMonitor de Notícias','heroTitle'));left.addWidget(lab('Acompanhe, analise e transforme informações em decisões.','heroSub'));left.addStretch();hl.addLayout(left,5)
        hl.addStretch(2)
        rail=lab('INFORMAÇÃO\nHOJE.\nDECISÕES\nAMANHÃ.','heroRail');rail.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft);hl.addWidget(rail,2)
        quote=lab('❞\nMais que monitoramento.\nInteligência para o seu tempo.','heroQuote');quote.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft);hl.addWidget(quote,3);root.addWidget(self.hero)

        self.metrics={};mrow=QHBoxLayout();mrow.setSpacing(9)
        specs=(('NEWS','Notícias','81','encontradas hoje','▤','#05bff6'),('VIDEOS','Vídeos','12','capturados hoje','▶','#a64cff'),('DEMANDS','Demandas','0','ativas','✉','#f2b51b'),('SOURCES','Fontes','160','cadastradas','◉','#1bd0df'),('TERMS','Termos','25','monitorados','⌕','#9d56ef'),('COVERS','Capas','8','jornais','▧','#28b9ea'),('PDF_EDITOR','Editor de PDF','—','ferramenta','▣','#2bb8d9'),('EXTRACTOR','Extrator de Vídeos','—','ferramenta','▦','#a65bed'),('VIDEO_EDITOR','Editor de Vídeo','—','ferramenta','✂','#ef4fb0'))
        for i,(key,title,value,sub,glyph,accent) in enumerate(specs):
            f=card('metric');f.setProperty('active','1' if i==0 else '0');f.setMinimumHeight(138);l=QVBoxLayout(f);l.setContentsMargins(14,12,10,10);l.setSpacing(4);g=lab(glyph);g.setStyleSheet(f'color:{accent};font-size:24px;font-weight:800;');l.addWidget(g);l.addStretch();l.addWidget(lab(title,'metricTitle'));v=lab(value,'metricValue');l.addWidget(v);l.addWidget(lab(sub,'metricSub'));self.metrics[key]=v
            b=QPushButton('',f);b.setCursor(Qt.CursorShape.PointingHandCursor);b.setStyleSheet('background:transparent;border:0;');b.clicked.connect(lambda _=False,k=key:self.navigate.emit(k));b.setGeometry(0,0,200,160);b.raise_();mrow.addWidget(f,1)
        root.addLayout(mrow)

        mid=QHBoxLayout();mid.setSpacing(10)
        mon=card('panel');ml=QVBoxLayout(mon);ml.setContentsMargins(16,12,16,12);ml.setSpacing(7);tr=QHBoxLayout();tr.addWidget(lab('⌁  Monitoramento em tempo real','panelTitle'));tr.addStretch();badge=lab('●  SISTEMA ATIVO');badge.setStyleSheet('color:#33e99b;background:#07583d;border-radius:8px;padding:4px 8px;font-size:8px;font-weight:800;');tr.addWidget(badge);ml.addLayout(tr);self.progress=QProgressBar();self.progress.setObjectName('homeProg');self.progress.setTextVisible(False);self.progress.setValue(100);ml.addWidget(self.progress);stat=QHBoxLayout();self.stat_labels=[]
        for val,name,color in [('100%','Conclusão','#20e9c5'),('76','Encontrados','#25d2eb'),('0','Novos','#ff3e53'),('0','Falhas','#b460ff'),('31/31','Etapas','#21bff3'),('00:00','Tempo','#20e9e2')]:
            box=QVBoxLayout();v=lab(val);v.setStyleSheet(f'font-size:16px;font-weight:800;color:{color};');n=lab(name,'metricSub');v.setAlignment(Qt.AlignmentFlag.AlignCenter);n.setAlignment(Qt.AlignmentFlag.AlignCenter);box.addWidget(v);box.addWidget(n);stat.addLayout(box,1);self.stat_labels.append(v)
        ml.addLayout(stat);mid.addWidget(mon,4)

        src=card('panel');sl=QVBoxLayout(src);sl.setContentsMargins(16,12,16,12);sl.addWidget(lab('▧  Fontes mais ativas hoje','panelTitle'));self.source_rows=[]
        for name,v in [('O Globo',18),('Folha de S.Paulo',12),('G1',9),('Correio Braziliense',8),('Revista Oeste',6)]:
            r=QHBoxLayout();r.addWidget(lab(name,'panelSub'),2);bar=QFrame();bar.setFixedHeight(5);bar.setStyleSheet('background:#0c3a56;border-radius:2px;');fill=QFrame(bar);fill.setGeometry(0,0,min(120,v*5),5);fill.setStyleSheet('background:#16c8ef;border-radius:2px;');r.addWidget(bar,2);r.addWidget(lab(str(v),'panelSub'));sl.addLayout(r)
        mid.addWidget(src,3)

        auto=card('panel');al=QVBoxLayout(auto);al.setContentsMargins(14,12,14,12);al.addWidget(lab('◷  Automação e agendamentos','panelTitle'));self.auto_lines={}
        for key,name in [('news','Notícias'),('demands','Demandas'),('videos','Vídeos')]:
            r=QHBoxLayout();r.addWidget(lab(name,'panelSub'));r.addStretch();state=lab('Ativo');state.setStyleSheet('color:#20e79d;border:1px solid #0a966c;border-radius:8px;padding:4px 9px;font-size:8px;');r.addWidget(state);al.addLayout(r);self.auto_lines[key]=state
        mid.addWidget(auto,3)

        tips=card('panel');tl=QVBoxLayout(tips);tl.setContentsMargins(14,12,14,12);tl.addWidget(lab('☀  Dicas do sistema','panelTitle'));tip=card('panel');tip.setStyleSheet('QFrame#panel{background:#07304b;border:1px solid #0b7da8;border-radius:9px;}');il=QVBoxLayout(tip);il.setContentsMargins(12,10,12,10);il.addWidget(lab('🚀  Use termos específicos','metricTitle'));il.addWidget(lab('Termos bem definidos trazem\nresultados mais relevantes.','panelSub'));tl.addWidget(tip);tl.addStretch();dots=lab('●  ●  ●');dots.setAlignment(Qt.AlignmentFlag.AlignCenter);dots.setStyleSheet('color:#1bbfe9;');tl.addWidget(dots);mid.addWidget(tips,3);root.addLayout(mid)

        bottom=QHBoxLayout();bottom.setSpacing(10)
        act=card('panel');actl=QVBoxLayout(act);actl.setContentsMargins(16,12,16,12);ar=QHBoxLayout();ar.addWidget(lab('⌁  Atividade recente','panelTitle'));ar.addStretch();ar.addWidget(lab('Ver histórico  →','panelSub'));actl.addLayout(ar);self.activity=[]
        for t,title,sub in [('13:24','Busca automática de notícias concluída','76 novas matérias encontradas'),('13:18','Captura de vídeos finalizada','12 vídeos processados'),('13:02','Atualização de capas concluída','8 jornais analisados'),('12:41','Sincronização de fontes','160 fontes verificadas'),('11:55','Sistema inicializado','Todos os módulos operacionais')]:
            r=QHBoxLayout();dot=lab('●');dot.setStyleSheet('color:#13c6de;font-size:15px;');r.addWidget(dot);r.addWidget(lab(t,'panelSub'));txt=QVBoxLayout();txt.addWidget(lab(title,'metricTitle'));txt.addWidget(lab(sub,'panelSub'));r.addLayout(txt,1);actl.addLayout(r);self.activity.append((title,sub))
        bottom.addWidget(act,4)
        pan=card('panel');pl=QVBoxLayout(pan);pl.setContentsMargins(16,12,16,12);pr=QHBoxLayout();pr.addWidget(lab('▦  Panorama das últimas 24 horas','panelTitle'));pr.addStretch();pr.addWidget(lab('■ Notícias   ■ Vídeos   ■ Demandas','panelSub'));pl.addLayout(pr);chart=MiniChart();chart.setMinimumHeight(120);pl.addWidget(chart,1);summ=QHBoxLayout();self.summary={}
        for key,g,val,name,color in [('news','▤','312','Total de notícias','#18c6ef'),('videos','▶','48','Total de vídeos','#a45df5'),('demands','✉','5','Demandas atendidas','#f4b61c')]:
            c=card('panel');cl=QHBoxLayout(c);cl.setContentsMargins(12,8,12,8);ic=lab(g);ic.setStyleSheet(f'color:{color};font-size:22px;');cl.addWidget(ic);tx=QVBoxLayout();v=lab(val,'metricValue');tx.addWidget(v);tx.addWidget(lab(name,'metricSub'));cl.addLayout(tx,1);summ.addWidget(c,1);self.summary[key]=v
        pl.addLayout(summ);bottom.addWidget(pan,6);root.addLayout(bottom,1)

    def refresh(self,state):
        news=len(state.news);videos=len(state.videos);demands=sum(1 for d in state.demands if getattr(d,'active',False));sources=len(self.controller.news_sources)
        for k,v in [('NEWS',news),('VIDEOS',videos),('DEMANDS',demands),('SOURCES',sources)]:self.metrics[k].setText(str(v))
        if 'news' in self.summary:self.summary['news'].setText(str(news))
        if 'videos' in self.summary:self.summary['videos'].setText(str(videos))
        if 'demands' in self.summary:self.summary['demands'].setText(str(demands))
        busy=bool(state.news_busy or state.video_busy);self.progress.setValue(55 if busy else 100);self.stat_labels[0].setText('55%' if busy else '100%');self.stat_labels[1].setText(str(news));self.stat_labels[2].setText('0');self.stat_labels[3].setText('0')
        auto=self.controller.automation_settings
        for state_label in self.auto_lines.values():state_label.setText('Ativo' if auto.automatic_monitoring else 'Pausado')
