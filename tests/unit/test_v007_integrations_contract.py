from __future__ import annotations

from pathlib import Path

from monitor_noticias.ui.sections import SECTION_ORDER, TOOL_SECTIONS, Section


ROOT = Path(__file__).resolve().parents[2]


def test_settings_is_always_last_sidebar_section() -> None:
    assert SECTION_ORDER[-1] is Section.SETTINGS
    assert SECTION_ORDER.index(Section.COVERS) < SECTION_ORDER.index(Section.SETTINGS)


def test_all_requested_integrations_have_distinct_sections() -> None:
    expected = {
        Section.PDF_EDITOR,
        Section.EXTRACTOR,
        Section.VIDEO_EDITOR,
        Section.NEWS_EXTRACTOR,
        Section.SHEET_AUTOMATION,
        Section.COVERS,
    }
    assert expected <= TOOL_SECTIONS
    assert len(SECTION_ORDER) == len(set(SECTION_ORDER))


def test_sidebar_and_video_editor_are_scrollable_by_contract() -> None:
    main_source = (ROOT / "src/monitor_noticias/ui/main_window.py").read_text(encoding="utf-8")
    tools_source = (ROOT / "src/monitor_noticias/ui/integrated_tools.py").read_text(encoding="utf-8")
    assert 'setObjectName("sidebarScroll")' in main_source
    assert "ScrollBarAsNeeded" in main_source
    assert "OriginalVideoEditorPage" in main_source
    assert "QScrollArea" in tools_source
    assert "editor.setMinimumSize(1120, 900)" in tools_source


def test_external_integrations_are_process_isolated() -> None:
    source = (ROOT / "src/monitor_noticias/ui/external_win32_page.py").read_text(encoding="utf-8")
    assert "subprocess.Popen" in source
    assert "Aplicativo encerrou" in source
    assert "QApplication.quit" not in source
    assert "SetParent" in source


def test_build_uses_exact_original_source_commits() -> None:
    source = (ROOT / "scripts/build_external_integrations.ps1").read_text(encoding="utf-8")
    for sha in (
        "ea43bb344d74dc2a32cc1d733aaabea54d763150",
        "51bd5386ea280edc2d56c6567be0113cfd84d2e5",
        "87705432008b00f114d27d1f1645c2c89e649365",
        "92f031c22cf8c23c2f5dd15a1857a6df4186b97e",
    ):
        assert sha in source
    assert "Copy-Original-Source $news" in source
    assert "Copy-Original-Source $sheet" in source
    assert "Copy-Original-Source $covers" in source
    assert 'Copy-Item (Join-Path $video "advanced_editor.py")' in source
    assert 'Copy-Item (Join-Path $video "range_slider.py")' in source
