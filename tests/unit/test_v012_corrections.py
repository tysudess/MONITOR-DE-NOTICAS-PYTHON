from __future__ import annotations

from pathlib import Path


def test_unique_parenthesized_keeps_original_and_increments(tmp_path: Path):
    from monitor_noticias.ui.v012_runtime_fixes import _unique_parenthesized

    original = tmp_path / "video.mp4"
    assert _unique_parenthesized(original) == original
    original.write_bytes(b"1")
    assert _unique_parenthesized(original).name == "video(1).mp4"
    (tmp_path / "video(1).mp4").write_bytes(b"1")
    assert _unique_parenthesized(original).name == "video(2).mp4"


def test_v012_is_installed_after_older_overlays():
    run = Path("run.py").read_text(encoding="utf-8")
    assert "install_v011_sidebar_fidelity()\n# v0.0.12" in run
    assert run.index("install_v011_sidebar_fidelity()") < run.index("install_v012_runtime_fixes()")


def test_external_overlay_has_ctrl_v_global_proxy_and_text_replacement_fix():
    patch = Path("scripts/patch_v012_external_integrations.py").read_text(encoding="utf-8")
    assert "Ctrl+V explícito" in patch
    assert "colarDoClipboard" in patch
    assert "readClipboard" in patch
    assert "legacyProxyControls" in patch
    assert "conexão única definida na aba Configurações do Monitor" in patch
    assert "inicio - 120" in patch
    assert "resultado.dispatchEvent(new Event('input'" in patch


def test_sidebar_finalizer_has_faithful_icons_and_removes_legacy_nodes():
    source = Path("src/monitor_noticias/ui/v012_runtime_fixes.py").read_text(encoding="utf-8")
    assert "QSvgRenderer" in source
    assert "sideGroupHeader" in source
    assert "FindDirectChildrenOnly" in source
    assert 'label.text().strip() == "●"' in source
    assert "badge.setParent(news_button)" in source
    for token in ("Section.HOME", "Section.NEWS", "Section.VIDEOS", "Section.PDF_EDITOR", "Section.SETTINGS"):
        assert token in source


def test_frontpages_fix_targets_current_washington_post_and_rejects_sports():
    source = Path("src/monitor_noticias/ui/v012_runtime_fixes.py").read_text(encoding="utf-8")
    assert "the-washington-post" in source
    assert "og:image" in source
    assert "currentSrc" in source
    assert "srcset" in source
    assert "sports" in source.lower()


def test_repeat_download_uses_fresh_directory_and_parenthesized_destination():
    source = Path("src/monitor_noticias/ui/v012_runtime_fixes.py").read_text(encoding="utf-8")
    assert 'tempfile.mkdtemp(prefix="monitor-download-"' in source
    assert "_unique_parenthesized(self.videos_dir / final.name)" in source
    assert "shutil.move" in source


def test_video_continuity_reasserts_play_after_media_load():
    source = Path("src/monitor_noticias/ui/v012_runtime_fixes.py").read_text(encoding="utf-8")
    assert "LoadedMedia" in source
    assert "BufferedMedia" in source
    assert "EndOfMedia" in source
    assert "editor.player.play()" in source
