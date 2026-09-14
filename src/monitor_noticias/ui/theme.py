from __future__ import annotations

# Contrato V5 público preservado: testes e módulos antigos dependem destes valores.
V5_NAVY = "#052D57"
V5_NAVY_DARK = "#031F3E"
V5_INK = "#0A1F4B"
V5_MUTED = "#58739F"
V5_BG = "#F3F8FE"
V5_BORDER = "#D5E4F3"
V5_BLUE = "#087AF7"
V5_PURPLE = "#743AF3"
V5_ORANGE = "#FF820A"
V5_GREEN = "#08A86F"
V5_RED = "#D92F43"
V5_GOLD = "#F2B715"
V5_SOFT_BLUE = "#EAF4FF"

# A paleta refinada fica encapsulada no stylesheet; não altera o contrato V5 acima.
APP_STYLESHEET = """
QMainWindow, QWidget#root { background:#031A2F; color:#F4F8FC; }
QWidget { font-family:'Segoe UI'; font-size:11px; color:#F4F8FC; }
QWidget#mainContent { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #03182b,stop:0.55 #032640,stop:1 #021426); }
QFrame#sidebar { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #052e50,stop:0.58 #042642,stop:1 #031a30); border:1px solid #087eae; border-radius:14px; }
QLabel#brandTitle { color:#ffffff; font-size:17px; font-weight:800; }
QLabel#brandSub { color:#a8c3db; font-size:10px; }
QLabel#anchorMark { color:#f5aa00; font-family:'Segoe UI Symbol'; font-size:46px; font-weight:700; }
QPushButton#navButton { color:#eef6ff; background:transparent; border:0; border-radius:9px; padding:9px 12px; text-align:left; font-size:13px; font-weight:500; }
QPushButton#navButton:hover { background:#083657; }
QPushButton#navButton:checked { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a659d,stop:1 #06375d); border:1px solid #00a9e8; color:#ffffff; font-weight:800; }
QLabel#newsBadge { color:#062440; background:#ffc21a; border-radius:10px; padding:2px 7px; font-size:9px; font-weight:800; }
QFrame#sideStatusCard { background:#052b48; border:1px solid #0a638d; border-radius:10px; }
QLabel#sideStatusTitle { color:#ffffff; font-size:10px; font-weight:800; }
QLabel#sideStatusText, QLabel#sideStatusGood { color:#a9c6df; font-size:9px; }
QLabel#sideMotto { color:#54bff2; font-size:8px; font-weight:700; letter-spacing:1px; }

QWidget#pageRoot { background:transparent; }
QFrame#pageHeader { background:transparent; border:0; }
QLabel#pageKicker { color:#67c9f4; font-size:10px; font-weight:700; letter-spacing:1.1px; }
QLabel#pageTitle { color:#ffffff; font-size:27px; font-weight:800; }
QLabel#pageSubtitle { color:#c1d3e5; font-size:12px; }
QLabel#pageIcon { color:#31bfff; font-size:37px; font-weight:700; }
QLabel#muted { color:#a8c2d8; }
QLabel#sectionTitle { color:#ffffff; font-size:18px; font-weight:800; }
QLabel#cardTitle { color:#ffffff; font-size:15px; font-weight:800; }
QLabel#smallTitle { color:#ffffff; font-size:12px; font-weight:700; }
QLabel#smallText { color:#b8cde0; font-size:10px; }
QLabel#blueText { color:#24aaff; font-weight:800; }
QLabel#greenText { color:#18e398; font-weight:800; }
QLabel#goldText { color:#ffc21a; font-weight:800; }
QLabel#purpleText { color:#bd78ff; font-weight:800; }
QLabel#redText { color:#ff5d68; font-weight:800; }

QFrame#card, QFrame#techCard, QFrame#resultCard, QFrame#filterCard, QFrame#settingsBlock { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #06375b,stop:0.52 #052d4b,stop:1 #031f38); border:1px solid #0a82b4; border-radius:12px; }
QFrame#resultCard:hover, QFrame#techCard:hover { border-color:#00b8ff; }
QFrame#statusCard { background:#063d57; border:1px solid #0fae83; border-radius:12px; }
QFrame#warningCard { background:#443714; border:1px solid #cf9e00; border-radius:10px; }
QFrame#dangerCard { background:#3a202a; border:1px solid #b73b4c; border-radius:10px; }
QFrame#emptyPanel { background:#052944; border:1px solid #0a82b4; border-radius:12px; }
QFrame#footerFrame { background:#03182b; border-top:1px solid #0a456b; }
QFrame#pillGreen { background:#063b3c; border:1px solid #05ba7a; border-radius:9px; }
QFrame#pillGold { background:#3b3517; border:1px solid #be9300; border-radius:9px; }
QFrame#pillBlue { background:#06385a; border:1px solid #087eae; border-radius:9px; }

QLineEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit { background:#052a46; color:#eef8ff; border:1px solid #0a8cc1; border-radius:9px; padding:8px 10px; min-height:26px; selection-background-color:#087af7; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus { border:1px solid #00c3ff; }
QComboBox::drop-down { border:0; width:22px; }

QPushButton { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #087af7,stop:1 #095ad2); color:white; border:1px solid #18b9f3; border-radius:9px; padding:8px 14px; font-weight:700; min-height:28px; }
QPushButton:hover { border-color:#62d8ff; background:#1086ff; }
QPushButton:pressed { background:#0653b8; }
QPushButton:disabled { background:#234258; color:#7390a6; border-color:#345369; }
QPushButton[secondary='true'] { background:#052945; color:#d9ecfb; border:1px solid #0a8cc1; }
QPushButton[secondary='true']:hover { background:#07395c; }
QPushButton[danger='true'] { background:#431f2a; color:#ff5b67; border:1px solid #e23f50; }
QPushButton[purple='true'] { background:#5d28b8; color:white; border:1px solid #a95dff; }
QPushButton[orange='true'] { background:#b76800; color:white; border:1px solid #ffad1f; }
QPushButton[green='true'] { background:#07865f; color:white; border:1px solid #16d99b; }
QPushButton[gold='true'] { background:#7a5900; color:#ffd43b; border:1px solid #dca900; }
QPushButton[ghost='true'] { background:transparent; color:#8fdcff; border:1px solid #0a83b8; }
QPushButton:checked { background:#116ef0; border-color:#41c9ff; }

QCheckBox { color:#e5f1fa; spacing:8px; }
QCheckBox::indicator { width:18px; height:18px; border:1px solid #67a7d6; border-radius:3px; background:#0c3957; }
QCheckBox::indicator:checked { background:#168dff; border-color:#49c9ff; }
QRadioButton { color:#e7f2fb; spacing:9px; min-height:26px; }
QRadioButton::indicator { width:18px; height:18px; border-radius:9px; border:2px solid #518bc0; background:#082e4d; }
QRadioButton::indicator:checked { background:#11d7f5; border:3px solid #0874a5; }

QProgressBar { border:0; border-radius:4px; background:#12384b; text-align:center; min-height:8px; max-height:8px; }
QProgressBar::chunk { background:#1de49b; border-radius:4px; }
QListWidget, QTableWidget { background:transparent; color:#eaf6ff; border:0; gridline-color:#0c557b; alternate-background-color:#05243d; outline:0; }
QListWidget::item { background:#063456; border:1px solid #0a6e99; border-radius:9px; padding:8px; margin:3px 0; }
QListWidget::item:selected { background:#0a5687; border-color:#16bff5; }
QHeaderView::section { background:#052944; color:#c8e0f1; padding:7px; border:0; border-bottom:1px solid #0a6088; font-weight:700; }
QScrollArea { border:0; background:transparent; }
QScrollArea QWidget#qt_scrollarea_viewport { background:transparent; }
QScrollBar:vertical { background:#031a2e; width:9px; margin:0; }
QScrollBar::handle:vertical { background:#0a5f86; min-height:32px; border-radius:4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QTabWidget::pane { border:0; background:transparent; }
QTabBar::tab { background:#052945; color:#d6e8f7; border:1px solid #0a79aa; padding:9px 18px; margin-right:7px; border-radius:8px; font-weight:700; }
QTabBar::tab:selected { background:#186be7; color:white; border-color:#4bcaff; }
QToolTip { background:#052d57; color:white; border:1px solid #0a82b4; }
"""
