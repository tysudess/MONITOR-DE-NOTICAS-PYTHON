from __future__ import annotations
_INSTALLED=False
FONT_QSS="QWidget,QLabel,QPushButton,QLineEdit,QComboBox,QSpinBox,QDateEdit,QTimeEdit,QTextEdit,QPlainTextEdit,QCheckBox,QRadioButton,QTableWidget,QListWidget,QTreeWidget{font-family:Arial;}"
def _apply(w):
    w.setStyleSheet(w.styleSheet()+"\n"+FONT_QSS)
    if getattr(w,'sidebar',None) is not None:w.sidebar.setFixedWidth(220)
    if getattr(w,'footer_widget',None) is not None:w.footer_widget.setFixedHeight(28)
    stack=getattr(w,'stack',None)
    if stack is not None and stack.currentWidget() is not None:
        p=stack.currentWidget();p.setStyleSheet(p.styleSheet()+"\n"+FONT_QSS)
def install_v015_font_fix():
    global _INSTALLED
    if _INSTALLED:return
    _INSTALLED=True
    from monitor_noticias.ui.main_window import MainWindow
    ob,on=MainWindow._build_ui,MainWindow.navigate
    def build(self):ob(self);_apply(self)
    def nav(self,s):on(self,s);_apply(self)
    MainWindow._build_ui=build;MainWindow.navigate=nav
