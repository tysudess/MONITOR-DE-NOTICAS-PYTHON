from __future__ import annotations

from pathlib import Path
import os, sys
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('MONITOR_DISABLE_WEATHER','1')
os.environ.setdefault('MONITOR_DISABLE_EXTERNAL_INTEGRATIONS','1')
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'
for p in (ROOT,SRC):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
import run  # noqa: F401,E402
from PySide6.QtWidgets import QApplication,QLineEdit
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import Section

def main()->int:
    app=QApplication.instance() or QApplication([])
    w=MainWindow();w._timer.stop();w.resize(1600,900);w.show();app.processEvents()
    if w.sidebar.width()!=218: raise RuntimeError(f'sidebar={w.sidebar.width()}')
    top=getattr(w,'reference_top_bar',None)
    if top is None or not top.isVisible(): raise RuntimeError('barra superior ausente')
    q=top.findChild(QLineEdit,'referenceGlobalSearch')
    if q is None: raise RuntimeError('busca global ausente')
    from monitor_noticias.ui.sections import Section
    for hidden in (Section.STOP,Section.NEWS_EXTRACTOR,Section.SHEET_AUTOMATION):
        holder=w.nav_holders.get(hidden)
        if holder is not None and holder.isVisible(): raise RuntimeError(f'navegação extra visível: {hidden.name}')
    out=ROOT/'artifacts'/'v015-image-truth';out.mkdir(parents=True,exist_ok=True)
    targets=((Section.HOME,'inicio'),(Section.NEWS,'noticias'),(Section.DEMANDS,'demandas'),(Section.SOURCES,'fontes'),(Section.TERMS,'termos'),(Section.SETTINGS,'configuracoes'),(Section.COVERS,'capas'),(Section.PDF_EDITOR,'editor-pdf'),(Section.EXTRACTOR,'extrator-videos'),(Section.VIDEO_EDITOR,'editor-video'))
    for section,name in targets:
        w.navigate(section);w._tick();app.processEvents()
        p=out/f'{name}-1600x900.png'
        if not w.grab().save(str(p),'PNG'): raise RuntimeError(str(p))
        print(f'SCREENSHOT={section.name}:{p}')
    w.navigate(Section.HOME);q.setText('teste visual');q.returnPressed.emit();app.processEvents()
    if w._current is not Section.NEWS: raise RuntimeError('busca global não roteou')
    nq=getattr(w.pages[Section.NEWS],'query',None)
    if nq is None or nq.text()!='teste visual': raise RuntimeError('busca global não preservou query real')
    w._allow_close=True;w.close();app.processEvents();return 0
if __name__=='__main__': raise SystemExit(main())
