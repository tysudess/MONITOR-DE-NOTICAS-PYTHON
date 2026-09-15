from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS", "1")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")


def test_v013_sidebar_overlay_is_last_and_visual_only():
    from pathlib import Path

    run = Path("run.py").read_text(encoding="utf-8")
    assert run.index("install_v012_runtime_fixes()") < run.index("install_v013_sidebar_reference()")

    source = Path("src/monitor_noticias/ui/v013_sidebar_reference.py").read_text(encoding="utf-8")
    assert "#021E35" in source
    assert "#164A6E" in source
    assert "#EDB707" in source
    assert "#FAC305" in source
    assert "border-left:6px solid #FAC305" in source
    assert "QPushButton#navButton:checked" in source
    assert "previous_build(self)" in source
    assert "previous_navigate(self, section)" in source
    assert "previous_tick(self)" in source
    # O overlay não pode chamar motores/controladores de negócio diretamente.
    for forbidden in (
        "stop_all_searches(",
        "search_news(",
        "search_videos(",
        "search_all_demands(",
        "proxy_config =",
        "automation_settings =",
    ):
        assert forbidden not in source


def test_v013_sidebar_runtime_preserves_navigation_and_reference_structure():
    import run  # noqa: F401 - instala os overlays na mesma ordem do executável.
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QFrame, QLabel, QScrollArea

    from monitor_noticias.app.paths import AppPaths
    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import SECTION_ORDER, Section

    app = QApplication.instance() or QApplication([])
    window = MainWindow(paths=AppPaths.discover())
    window._timer.stop()
    window.show()
    app.processEvents()

    try:
        assert window.sidebar.width() == 318
        scroll = window.sidebar.findChild(QScrollArea, "sidebarScroll")
        assert scroll is not None
        assert scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        assert scroll.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded

        headers = window.sidebar.findChildren(QFrame, "sideGroupHeader")
        titles = [label.text() for frame in headers for label in frame.findChildren(QLabel, "sideGroupTitle")]
        assert titles == ["PRINCIPAL", "GERENCIAMENTO", "FERRAMENTAS", "SISTEMA"]

        assert tuple(window.nav_buttons) == SECTION_ORDER
        heights = {button.height() for button in window.nav_buttons.values()}
        assert heights == {54}
        assert all(not button.icon().isNull() for button in window.nav_buttons.values())

        for section in SECTION_ORDER:
            window.navigate(section)
            app.processEvents()
            checked = [sec for sec, button in window.nav_buttons.items() if button.isChecked()]
            assert checked == [section]
            assert all("❯" not in button.text() for button in window.nav_buttons.values())
            assert window.stack.currentIndex() == SECTION_ORDER.index(section)

        assert window.sidebar.findChild(QLabel, "sideStatusRing") is not None
        assert window.sidebar.findChild(QLabel, "sideStatusBars") is not None
        assert window.sidebar.findChild(QLabel, "sideWindowsIcon") is not None
        assert "●" not in window.side_status_title.text()

        window._tick()
        app.processEvents()
        assert window.side_status_title.text() in {"Busca em andamento", "Sistema operacional"}
        assert window.side_proxy.text().strip()
        assert window.side_automation.text().strip()
        assert window.side_status_card.findChild(QLabel, "sideStatusRing") is not None

        version_labels = [
            label.text()
            for label in window.side_status_card.findChildren(QLabel)
            if "Windows Portable" in label.text()
        ]
        assert len(version_labels) == 1
        assert version_labels[0].startswith("Windows Portable")
    finally:
        window._allow_close = True
        window.close()
        app.processEvents()
