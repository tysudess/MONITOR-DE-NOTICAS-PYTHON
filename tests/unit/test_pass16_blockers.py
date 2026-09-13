from __future__ import annotations

from pathlib import Path

from monitor_noticias.extractor import login_helper


def test_bundled_globoplay_helper_materializes_resource_to_runtime(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(login_helper, "MIN_HELPER_SIZE", 8)
    source = tmp_path / "resources" / "globoplay-login-helper" / "GloboplayLoginHelper.exe"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"0123456789abcdef")

    target = login_helper.resolve_bundled_helper(tmp_path)

    assert target == tmp_path / "data" / "extractor" / "runtime" / "GloboplayLoginHelper.exe"
    assert target.read_bytes() == source.read_bytes()


def test_bundled_globoplay_helper_does_not_fallback_to_external_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(login_helper, "MIN_HELPER_SIZE", 1)
    external = tmp_path / "data" / "extractor" / "runtime" / "GloboplayLoginHelper.exe"
    external.parent.mkdir(parents=True)
    external.write_bytes(b"already-there")

    try:
        login_helper.resolve_bundled_helper(tmp_path)
    except FileNotFoundError as exc:
        assert "/globoplay-login-helper/GloboplayLoginHelper.exe ausente" in str(exc)
    else:
        raise AssertionError("O runtime não pode substituir o resource empacotado da baseline Kotlin.")
