from __future__ import annotations

# Runtime hook de EMPACOTAMENTO. No uso normal é um no-op. Somente a workflow
# do portable define MONITOR_PORTABLE_SMOKE=1 para validar o próprio runtime
# congelado, sem Python do sistema e sem alterar o fluxo normal de run.py.
import os

if os.environ.get("MONITOR_PORTABLE_SMOKE") == "1":
    import json
    from pathlib import Path
    import subprocess
    import sys
    import time
    import traceback

    root = Path(sys.executable).resolve().parent
    result_path = Path(os.environ.get("MONITOR_PORTABLE_SMOKE_RESULT", str(root / "temp" / "portable-smoke-result.json")))
    result_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {"ok": False, "root": str(root)}

    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtMultimedia import QMediaPlayer
        from PySide6.QtWidgets import QApplication
        from pypdf import PdfReader

        from monitor_noticias.app.paths import AppPaths
        from monitor_noticias.pdf_editor.core import PdfEditorModel
        from monitor_noticias.ui.main_window import MainWindow
        from monitor_noticias.ui.sections import SECTION_ORDER, Section
        from monitor_noticias.video_editor.core import Clip, build_export_command, probe_video

        app = QApplication.instance() or QApplication([])
        paths = AppPaths(root)
        paths.ensure_runtime_dirs()

        # UI real empacotada: constrói todas as páginas e navega pelo mesmo stack.
        main = MainWindow(paths=paths)
        navigated: list[str] = []
        for section in SECTION_ORDER:
            main.navigate(section)
            app.processEvents()
            navigated.append(section.name)

        # PDF: motor real com documento artificial, salvo dentro da raiz portable.
        pdf_model = PdfEditorModel(root)
        pdf_model.clear_all()
        pdf_model.create_blank_page()
        pdf_output = root / "temp" / "portable-smoke.pdf"
        pdf_model.export_pdf(pdf_output, include_cover=False)
        if not pdf_output.is_file() or len(PdfReader(str(pdf_output)).pages) != 1:
            raise RuntimeError("Editor PDF empacotado não gerou PDF artificial válido.")

        ffmpeg = root / "bin" / "ffmpeg.exe"
        ffprobe = root / "bin" / "ffprobe.exe"
        if not ffmpeg.is_file() or not ffprobe.is_file():
            raise RuntimeError("FFmpeg/FFprobe próprios ausentes.")

        media_dir = root / "temp" / "portable-media-smoke"
        media_dir.mkdir(parents=True, exist_ok=True)
        source = media_dir / "fonte teste edição.mp4"
        exported = media_dir / "saida corte.mp4"

        def run(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
            cp = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
            if cp.returncode != 0:
                raise RuntimeError(f"Comando falhou ({cp.returncode}): {command}\n{cp.stdout}\n{cp.stderr}")
            return cp

        run([
            str(ffmpeg), "-y",
            "-f", "lavfi", "-i", "testsrc=size=320x240:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=44100",
            "-t", "2.0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(source),
        ])

        info = probe_video(source, ffprobe)
        if not (1800 <= info.duration_ms <= 2200 and info.width == 320 and info.height == 240):
            raise RuntimeError(f"FFprobe empacotado retornou mídia inesperada: {info}")

        # Abre o editor A PARTIR do workspace do Monitor real empacotado.
        video_page = main.pages[Section.VIDEO_EDITOR]
        video_page.open_editor()
        app.processEvents()
        if not video_page._windows:
            raise RuntimeError("Workspace do Monitor não abriu o Editor de Vídeo real.")
        editor = video_page._windows[-1]
        editor.clips.append(Clip(path=source, info=info))
        editor.refresh_media()
        editor.select_clip(0)
        editor.seek_global(0)
        app.processEvents()

        editor.player.play()
        deadline = time.monotonic() + 8.0
        max_position = 0
        while time.monotonic() < deadline:
            app.processEvents()
            max_position = max(max_position, editor.player.position())
            if editor.player.error() != QMediaPlayer.Error.NoError:
                raise RuntimeError("QMediaPlayer empacotado: " + editor.player.errorString())
            if max_position >= 300:
                break
            time.sleep(0.02)
        if max_position < 300:
            raise RuntimeError(f"Preview empacotado não avançou: {max_position} ms")

        editor.player.pause()
        app.processEvents()
        if editor.player.playbackState() != QMediaPlayer.PlaybackState.PausedState:
            raise RuntimeError("Pause do player empacotado falhou.")
        editor.seek_global(1000)
        seek_deadline = time.monotonic() + 3.0
        while time.monotonic() < seek_deadline:
            app.processEvents()
            if abs(editor.player.position() - 1000) <= 250:
                break
            time.sleep(0.02)
        seek_position = editor.player.position()
        if abs(seek_position - 1000) > 250:
            raise RuntimeError(f"Seek empacotado fora da tolerância: {seek_position} ms")
        if abs(editor.audio.volume() - 0.85) >= 0.01:
            raise RuntimeError("Volume inicial empacotado divergiu de 0.85.")

        command = build_export_command(ffmpeg, editor.clips[0], exported)
        run(command, timeout=120)
        if not exported.is_file() or exported.stat().st_size <= 1024:
            raise RuntimeError("Exportação FFmpeg empacotada não gerou arquivo.")
        exported_info = probe_video(exported, ffprobe)
        if exported_info.video_codec != "h264" or exported_info.audio_codec != "aac":
            raise RuntimeError(f"Exportação empacotada divergente: {exported_info}")

        # Extrator real: os cinco binários e o helper resource devem ser resolvidos.
        extractor = main.pages[Section.EXTRACTOR]
        binaries = {
            "yt_dlp": extractor.engine.yt_dlp.is_file(),
            "yt_dlp_stable": extractor.engine.yt_dlp_stable.is_file(),
            "deno": extractor.engine.deno.is_file(),
            "ffmpeg": extractor.engine.ffmpeg.is_file(),
            "ffprobe": extractor.engine.ffprobe.is_file(),
        }
        if not all(binaries.values()):
            raise RuntimeError(f"Binários do Extrator incompletos: {binaries}")
        helper_resource = root / "resources" / "globoplay-login-helper" / "GloboplayLoginHelper.exe"
        if not helper_resource.is_file() or helper_resource.stat().st_size <= 20_000_000:
            raise RuntimeError("Helper Globoplay empacotado ausente/incompleto.")

        # Teardown real das ferramentas integradas, inclusive liberação do handle.
        if not video_page.shutdown():
            raise RuntimeError("Shutdown do Editor de Vídeo empacotado falhou.")
        if not extractor.shutdown():
            raise RuntimeError("Shutdown do Extrator empacotado falhou.")
        editor.player.setSource(QUrl())
        for _ in range(5):
            app.processEvents(); time.sleep(0.02)
        source.unlink()
        if source.exists():
            raise RuntimeError("QMediaPlayer empacotado manteve handle da mídia.")

        main._allow_close = True
        main._timer.stop()
        main.controller.close()
        main.tray.hide()
        main.close()
        app.processEvents()

        payload.update({
            "ok": True,
            "navigated": navigated,
            "pdf": str(pdf_output),
            "player_position_ms": max_position,
            "seek_position_ms": seek_position,
            "video_codec": exported_info.video_codec,
            "audio_codec": exported_info.audio_codec,
            "resolution": f"{exported_info.width}x{exported_info.height}",
            "fps": exported_info.fps,
            "binaries": binaries,
        })
        result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os._exit(0)
    except BaseException as exc:
        payload.update({"ok": False, "error": str(exc), "traceback": traceback.format_exc()})
        try:
            result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        finally:
            os._exit(91)
