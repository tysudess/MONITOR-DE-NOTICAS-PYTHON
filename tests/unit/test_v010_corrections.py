from __future__ import annotations

import os
from types import SimpleNamespace

from monitor_noticias.ui.v010_runtime_fixes import _proxy_url, _sync_proxy_environment


def test_global_proxy_url_is_single_source_and_encodes_credentials(monkeypatch):
    cfg = SimpleNamespace(
        enabled=True,
        host="proxy-7dn.mb",
        port=6060,
        username="usuario dom",
        password="s@nh:a",
    )
    expected = "http://usuario%20dom:s%40nh%3Aa@proxy-7dn.mb:6060"
    assert _proxy_url(cfg) == expected
    assert _sync_proxy_environment(cfg) == expected
    assert os.environ["HTTP_PROXY"] == expected
    assert os.environ["HTTPS_PROXY"] == expected
    assert os.environ["MONITOR_PROXY_URL"] == expected


def test_disabling_global_proxy_clears_monitor_proxy_environment(monkeypatch):
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "MONITOR_PROXY_URL"):
        monkeypatch.setenv(key, "http://old-proxy:9999")
    cfg = SimpleNamespace(enabled=False, host="proxy-7dn.mb", port=6060, username="", password="")
    assert _sync_proxy_environment(cfg) == ""
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "MONITOR_PROXY_URL"):
        assert key not in os.environ


def test_v010_runtime_contains_requested_safety_and_navigation_contracts():
    import inspect
    import monitor_noticias.ui.v010_runtime_fixes as fixes

    source = inspect.getsource(fixes)
    assert "_v010_preview_jobs" in source
    assert "QMediaPlayer.MediaStatus.EndOfMedia" in source
    assert "GoogleNewsUrlResolver" in source
    assert "send_news_to_extractor" in source
    assert "send_video_to_extractor" in source
    assert '("PRINCIPAL", Section.HOME)' in source
    assert '("GERENCIAMENTO", Section.DEMANDS)' in source
    assert '("FERRAMENTAS", Section.PDF_EDITOR)' in source
    assert '("SISTEMA", Section.SETTINGS)' in source


def test_external_overlay_removes_individual_proxy_and_adds_monitor_url_bridge():
    from pathlib import Path

    patch = Path("scripts/patch_v010_external_integrations.py").read_text(encoding="utf-8")
    assert "MONITOR_PROXY_URL" in patch
    assert "monitor-url.txt" in patch
    assert "onMonitorUrl" in patch
    assert "Colar" in patch
    assert 'style=\\"display:none\\"' in patch


def test_entrypoint_installs_v010_fixes_and_electron_bridge():
    from pathlib import Path

    run = Path("run.py").read_text(encoding="utf-8")
    assert "install_v010_runtime_fixes()" in run
    assert "install_v010_external_bridge()" in run
