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
from PySide6.QtWidgets import QApplication
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import Section, SECTION_ORDER
from monitor_noticias.ui.home_dashboard import HomeDashboard
from monitor_noticias.ui.refined_pages import NewsPage, VideosPage, DemandsPage, SourcesPage, HistoryPage, TermsPage, StopPage, SettingsPage
from monitor_noticias.ui.refined_tools import RefinedExtractorPage, RefinedPdfEditorPage
from monitor_noticias.ui.integrated_tools import CoversPage, OriginalVideoEditorPage
from monitor_noticias.ui.external_win32_page import ExternalWin32AppPage

EXPECTED={
    Section.HOME: HomeDashboard,
    Section.NEWS: NewsPage,
    Section.VIDEOS: VideosPage,
    Section.DEMANDS: DemandsPage,
    Section.SOURCES: SourcesPage,
    Section.HISTORY: HistoryPage,
    Section.TERMS: TermsPage,
    Section.STOP: StopPage,
    Section.PDF_EDITOR: RefinedPdfEditorPage,
    Section.EXTRACTOR: RefinedExtractorPage,
    Section.VIDEO_EDITOR: OriginalVideoEditorPage,
    Section.NEWS_EXTRACTOR: ExternalWin32AppPage,
    Section.SHEET_AUTOMATION: ExternalWin32AppPage,
    Section.COVERS: CoversPage,
    Section.SETTINGS: SettingsPage,
}

def main()->int:
    app=QApplication.instance() or QApplication([])
    w=MainWindow(); w._timer.stop(); w.resize(1600,900); w.show(); app.processEvents()

    # Gate principal: nenhuma pagina funcional pode ter sido substituida pelo layout.
    for section,cls in EXPECTED.items():
        page=w.pages.get(section)
        if not isinstance(page,cls):
            raise RuntimeError(f'pagina substituida: {section.name}: {type(page).__name__} != {cls.__name__}')

    # Todas as funcionalidades cadastradas devem continuar visiveis na navegacao.
    missing=[]
    for section in SECTION_ORDER:
        holder=w.nav_holders.get(section)
        button=w.nav_buttons.get(section)
        if holder is None or button is None:
            missing.append(section.name); continue
        if holder.isHidden() or not holder.isVisible():
            missing.append(section.name)
    if missing:
        raise RuntimeError('abas ocultas: '+','.join(missing))

    # Gate explicito solicitado: Extrator de Noticias e Automacao Planilhas presentes.
    for section in (Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION):
        w.navigate(section); app.processEvents()
        if w._current is not section or w.stack.currentWidget() is not w.pages[section]:
            raise RuntimeError(f'navegacao quebrada: {section.name}')

    out=ROOT/'artifacts'/'v016-layout-only'; out.mkdir(parents=True,exist_ok=True)
    targets=((Section.HOME,'inicio'),(Section.NEWS,'noticias'),(Section.DEMANDS,'demandas'),(Section.SOURCES,'fontes'),(Section.TERMS,'termos'),(Section.SETTINGS,'configuracoes'),(Section.COVERS,'capas'),(Section.PDF_EDITOR,'editor-pdf'),(Section.EXTRACTOR,'extrator-videos'),(Section.VIDEO_EDITOR,'editor-video'),(Section.NEWS_EXTRACTOR,'extrator-noticias'),(Section.SHEET_AUTOMATION,'automacao-planilhas'))
    for section,name in targets:
        w.navigate(section); w._tick(); app.processEvents()
        p=out/f'{name}-1600x900.png'
        if not w.grab().save(str(p),'PNG'): raise RuntimeError(str(p))
        print(f'SCREENSHOT={section.name}:{p}')

    # Confirma que o layout novo nao instala as camadas v0.0.15 que substituiam/ocultavam UI.
    text=(ROOT/'run.py').read_text(encoding='utf-8')
    for forbidden in ('install_v015_image_truth_layout()', 'install_v015_home_reference()'):
        if forbidden in text:
            raise RuntimeError(f'camada estrutural proibida ainda ativa: {forbidden}')
    if 'install_v016_layout_only()' not in text:
        raise RuntimeError('camada v0.0.16 nao ativa')

    w._allow_close=True; w.close(); app.processEvents(); return 0

if __name__=='__main__': raise SystemExit(main())
