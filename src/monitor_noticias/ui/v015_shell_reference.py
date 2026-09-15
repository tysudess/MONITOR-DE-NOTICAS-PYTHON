from __future__ import annotations

from PySide6.QtCore import QPointF,QRectF,Qt
from PySide6.QtGui import QColor,QPainter,QPen,QLinearGradient

_INSTALLED=False

def _paint(self,event):
    from PySide6.QtWidgets import QFrame
    QFrame.paintEvent(self,event)
    p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
    w,h=self.width(),self.height();cx=w*.48;cy=h*.58;r=h*.95
    glow=QLinearGradient(cx-r,cy-r,cx+r,cy+r);glow.setColorAt(0,QColor(0,35,65,0));glow.setColorAt(.48,QColor(0,102,185,70));glow.setColorAt(1,QColor(0,25,60,0))
    p.setPen(Qt.PenStyle.NoPen);p.setBrush(glow);p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
    p.setBrush(Qt.BrushStyle.NoBrush)
    for rr,a in ((r*.88,105),(r*.68,85),(r*.48,72),(r*.28,62)):
        p.setPen(QPen(QColor(0,160,255,a),1));p.drawEllipse(QPointF(cx,cy),rr,rr*.53)
    p.setPen(QPen(QColor(0,130,220,72),1))
    for dx in (-.43,-.20,0,.20,.43):
        x=cx+dx*r*.60;p.drawArc(QRectF(x-r*.52,cy-r*.72,r*1.04,r*1.44),70*16,220*16)
    p.setPen(QPen(QColor(20,188,255,100),1))
    nodes=((.36,.30,.45,.42),(.44,.42,.54,.28),(.50,.58,.61,.44),(.39,.68,.53,.58),(.58,.28,.68,.35),(.57,.66,.70,.54))
    for x1,y1,x2,y2 in nodes:
        a=QPointF(w*x1,h*y1);b=QPointF(w*x2,h*y2);p.drawLine(a,b);p.drawEllipse(b,2.2,2.2)
    p.setPen(QPen(QColor(0,120,185,48),1))
    for i in range(8):p.drawLine(QPointF(w*(.28+i*.045),0),QPointF(w*(.40+i*.055),h))
    p.setPen(QPen(QColor(0,203,255,190),2));p.drawLine(QPointF(w*.69,h*.76),QPointF(w*.77,h*.76))


def install_v015_shell_reference()->None:
    global _INSTALLED
    if _INSTALLED:return
    _INSTALLED=True
    from monitor_noticias.ui.refined_shell import RadarHeader
    old_set=RadarHeader.set_section
    RadarHeader.paintEvent=_paint
    def set_section(self,title,subtitle):
        old_set(self,title,subtitle)
        self.setMinimumHeight(132);self.setMaximumHeight(142)
        self.kicker.setText('')
        self.title.setStyleSheet('color:#ffffff;font-size:29px;font-weight:800;background:transparent;')
        self.subtitle.setStyleSheet('color:#c5d5e5;font-size:12px;background:transparent;')
        icon_titles={'Configurações','Editor de PDF','Editor de Vídeo'}
        if title in icon_titles:
            self.icon.show();self.icon.setFixedWidth(72)
        else:
            self.icon.hide();self.icon.setFixedWidth(0)
    RadarHeader.set_section=set_section
