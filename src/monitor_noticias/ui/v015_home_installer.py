from __future__ import annotations

_INSTALLED=False

def install_v015_home_reference()->None:
    global _INSTALLED
    if _INSTALLED:return
    _INSTALLED=True
    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v015_home_reference import ReferenceHomePage
    old_build=MainWindow._build_ui
    def build(self):
        old_build(self)
        old=self.pages[Section.HOME]
        idx=self.stack.indexOf(old)
        page=ReferenceHomePage(self.controller)
        page.navigate.connect(lambda name:self.navigate(Section[name]))
        self.stack.removeWidget(old)
        old.setParent(None)
        self.stack.insertWidget(idx,page)
        self.pages[Section.HOME]=page
    MainWindow._build_ui=build
