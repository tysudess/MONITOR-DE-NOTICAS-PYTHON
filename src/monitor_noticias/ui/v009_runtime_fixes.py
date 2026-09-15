from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import types

from PySide6.QtCore import QProcess, QProcessEnvironment, QTimer, QUrl
from PySide6.QtWidgets import QScrollArea

log = logging.getLogger(__name__)
_INSTALLED = False


def _kill_process_tree(process: QProcess | None) -> None:
    if process is None:
        return
    try:
        pid = int(process.processId())
    except Exception:
        pid = 0
    if pid > 0 and os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            subprocess.run(
                ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
                check=False,
                shell=False,
                creationflags=flags,
            )
        except Exception:
            log.exception("Falha ao encerrar árvore do worker isolado do Extrator")
    try:
        if process.state() != QProcess.ProcessState.NotRunning:
            process.kill()
            process.waitForFinished(2500)
    except RuntimeError:
        pass


def _worker_program_and_args(app_root: Path, url: str, quality_index: int) -> tuple[str, list[str]]:
    args = [
        "--extractor-worker",
        "--app-root", str(Path(app_root)),
        "--url", url,
        "--quality-index", str(int(quality_index)),
    ]
    if getattr(sys, "frozen", False):
        return sys.executable, args
    return sys.executable, [str(Path(app_root) / "run.py"), *args]


def _patch_sidebar() -> None:
    from monitor_noticias.ui.main_window import MainWindow

    if getattr(MainWindow, "_v009_sidebar_patched", False):
        return
    original_navigate = MainWindow.navigate
    original_build_ui = MainWindow._build_ui

    def build_ui(self):
        original_build_ui(self)
        scroll = self.sidebar.findChild(QScrollArea, "sidebarScroll")
        self._v009_sidebar_scroll = scroll
        for holder in self.nav_holders.values():
            holder.setVisible(True)
        if scroll is not None:
            scroll.setWidgetResizable(True)
            QTimer.singleShot(0, lambda s=scroll: s.verticalScrollBar().setValue(s.verticalScrollBar().minimum()))

    def navigate(self, section):
        original_navigate(self, section)
        # V8 ocultava as ferramentas na HOME. Por isso elas só apareciam depois
        # do primeiro clique em outra aba. Em V9 toda a navegação fica disponível
        # desde a abertura; o scroll lateral cuida de janelas menores.
        for holder in self.nav_holders.values():
            holder.setVisible(True)
        scroll = getattr(self, "_v009_sidebar_scroll", None)
        if scroll is not None and not getattr(self, "_v009_sidebar_initialized", False):
            self._v009_sidebar_initialized = True
            QTimer.singleShot(0, lambda s=scroll: s.verticalScrollBar().setValue(s.verticalScrollBar().minimum()))

    MainWindow._build_ui = build_ui
    MainWindow.navigate = navigate
    MainWindow._v009_sidebar_patched = True


def _patch_native_host_dpi() -> None:
    from monitor_noticias.ui.external_win32_page import _NativeHost

    if getattr(_NativeHost, "_v009_dpi_patched", False):
        return

    def resize_child(self) -> None:
        if os.name != "nt" or not getattr(self, "_child_hwnd", 0):
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = int(self._child_hwnd)
            if not user32.IsWindow(hwnd):
                return
            # Qt fornece pixels lógicos; Electron hospedado recebe pixels físicos
            # em DPI per-monitor. A ausência desta conversão deixava ~20% da aba
            # vazia em escalas de 125% e 150%.
            dpr = max(1.0, float(self.devicePixelRatioF()))
            width = max(1, int(round(self.width() * dpr)))
            height = max(1, int(round(self.height() * dpr)))
            flags = 0x0004 | 0x0010 | 0x0040  # NOZORDER | NOACTIVATE | SHOWWINDOW
            user32.SetWindowPos(hwnd, 0, 0, 0, width, height, flags)
            user32.MoveWindow(hwnd, 0, 0, width, height, True)
        except Exception:
            log.exception("Falha ao redimensionar janela externa incorporada com DPI")

    _NativeHost._resize_child = resize_child
    _NativeHost._v009_dpi_patched = True


def _patch_extractor_isolation() -> None:
    from monitor_noticias.ui.extractor_page import ExtractorPage
    from monitor_noticias.extractor import EXTRACTOR_QUALITIES

    if getattr(ExtractorPage, "_v009_isolation_patched", False):
        return

    original_shutdown = ExtractorPage.shutdown

    def start_download(self) -> None:
        clean_url = self.url.text().strip()
        existing = getattr(self, "_isolated_download_process", None)
        if not clean_url or (existing is not None and existing.state() != QProcess.ProcessState.NotRunning):
            return

        self._operation_token += 1
        token = self._operation_token
        index = self._quality_index()
        self.state_store.save_quality_index(index)
        self.progress.setValue(0)
        self.percent.setText("0%")
        self.status.setText(f"Iniciando download isolado em {EXTRACTOR_QUALITIES[index].label}...")
        self._set_busy(True)

        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUTF8", "1")
        env.insert("MONITOR_EXTRACTOR_ISOLATED", "1")
        process.setProcessEnvironment(env)
        process.setWorkingDirectory(str(self.app_root))
        self._isolated_download_process = process
        self._isolated_download_buffer = ""
        self._isolated_download_terminal = False

        program, args = _worker_program_and_args(self.app_root, clean_url, index)

        def read_stdout() -> None:
            if token != self._operation_token:
                return
            chunk = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
            self._isolated_download_buffer += chunk
            parts = self._isolated_download_buffer.splitlines(keepends=True)
            self._isolated_download_buffer = ""
            for part in parts:
                if not part.endswith(("\n", "\r")):
                    self._isolated_download_buffer += part
                    continue
                line = part.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                kind = str(payload.get("type", ""))
                if kind == "progress":
                    self._download_progress(token, int(payload.get("pct", 0)), str(payload.get("message", "")))
                elif kind == "done":
                    self._isolated_download_terminal = True
                    self._download_success(token, str(payload.get("path", "")))
                elif kind == "error":
                    self._isolated_download_terminal = True
                    self._download_failure(token, str(payload.get("message", "Falha no download.")))

        def finished(exit_code: int, _status) -> None:
            read_stdout()
            if token == self._operation_token and not self._isolated_download_terminal:
                err = bytes(process.readAllStandardError()).decode("utf-8", errors="replace").strip()
                message = err[-1800:] if err else f"O processo isolado do Extrator encerrou com código {exit_code}."
                self._download_failure(token, message)
            if getattr(self, "_isolated_download_process", None) is process:
                self._isolated_download_process = None
            try:
                process.deleteLater()
            except RuntimeError:
                pass

        def failed(_error) -> None:
            if token == self._operation_token:
                self._isolated_download_terminal = True
                self._download_failure(token, process.errorString() or "Não foi possível iniciar o Extrator isolado.")

        process.readyReadStandardOutput.connect(read_stdout)
        process.finished.connect(finished)
        process.errorOccurred.connect(failed)
        process.start(program, args)

    def cancel_download(self) -> None:
        process = getattr(self, "_isolated_download_process", None)
        if process is None or process.state() == QProcess.ProcessState.NotRunning:
            return
        self._operation_token += 1
        _kill_process_tree(process)
        self._isolated_download_process = None
        self._set_busy(False)
        self.status.setText("Download cancelado.")

    def shutdown(self, timeout_ms: int = 5000) -> bool:
        process = getattr(self, "_isolated_download_process", None)
        if process is not None and process.state() != QProcess.ProcessState.NotRunning:
            self._operation_token += 1
            _kill_process_tree(process)
            self._isolated_download_process = None
        return original_shutdown(self, timeout_ms)

    ExtractorPage.start_download = start_download
    ExtractorPage.cancel_download = cancel_download
    ExtractorPage.shutdown = shutdown
    ExtractorPage._v009_isolation_patched = True


class _PreviewCompatController:
    """Cria proxy H.264 somente para prévia; edição/exportação usam o original."""

    def __init__(self, page, editor) -> None:
        self.page = page
        self.editor = editor
        self.probes: dict[str, QProcess] = {}
        self.transcodes: dict[str, QProcess] = {}
        self.forced: set[str] = set()
        self.cache_dir = Path(page.app_root) / "temp" / "video-preview-proxy"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._install_seek_wrapper()
        try:
            editor.player.errorOccurred.connect(lambda *_: self.force_current())
            editor.player.mediaStatusChanged.connect(self._media_status_changed)
        except Exception:
            log.exception("Falha ao conectar fallback de prévia")

    def _source_key(self, path: str) -> str:
        p = Path(path)
        try:
            stat = p.stat()
            token = f"{p.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
        except Exception:
            token = str(p)
        return hashlib.sha256(token.encode("utf-8", errors="replace")).hexdigest()[:24]

    def _current_index(self) -> int:
        idx = int(getattr(self.editor, "preview_clip_index", -1))
        if 0 <= idx < len(getattr(self.editor, "clips", [])):
            return idx
        idx = int(getattr(self.editor, "selected_index", -1))
        return idx if 0 <= idx < len(getattr(self.editor, "clips", [])) else -1

    def _install_seek_wrapper(self) -> None:
        controller = self

        def seek_sequence(editor_self, global_ms, keep_playing=False):
            if not editor_self.clips:
                return
            total = editor_self.total_duration_ms()
            global_ms = max(0, min(int(global_ms), total))
            if global_ms >= total and total > 0:
                global_ms = max(0, total - 1)
            mapped = editor_self.map_global(global_ms)
            if not mapped:
                return
            idx, source_ms = mapped
            editor_self.global_playhead_ms = global_ms
            editor_self.preview_clip_index = idx
            clip = editor_self.clips[idx]
            editor_self.preview_clip_end_source_ms = int(clip["end_ms"])
            editor_self._pending_seek_ms = int(source_ms)
            editor_self._pending_autoplay = bool(keep_playing)
            controller.prepare(idx)
            preview_path = str(clip.get("_preview_path") or clip["path"])
            current = editor_self.player.source().toLocalFile() if not editor_self.player.source().isEmpty() else ""
            if Path(current) != Path(preview_path):
                editor_self.player.setSource(QUrl.fromLocalFile(preview_path))
            else:
                editor_self._apply_pending_seek()
            editor_self._update_global_ui(auto_scroll=True)

        self.editor.seek_sequence = types.MethodType(seek_sequence, self.editor)

    def prepare(self, index: int, force: bool = False) -> None:
        if not (0 <= index < len(self.editor.clips)):
            return
        clip = self.editor.clips[index]
        source = str(clip.get("path", ""))
        if not source or clip.get("_preview_path"):
            return
        key = self._source_key(source)
        proxy = self.cache_dir / f"{key}.mp4"
        if proxy.is_file() and proxy.stat().st_size > 1024:
            clip["_preview_path"] = str(proxy)
            return
        if force:
            self.forced.add(key)
            self._start_proxy(index, key, source, proxy)
            return
        if key in self.probes or key in self.transcodes:
            return
        ffprobe = Path(self.editor.ffprobe_exe)
        if not ffprobe.is_file():
            return
        proc = QProcess(self.page)
        proc.setProgram(str(ffprobe))
        proc.setArguments([
            "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,pix_fmt",
            "-of", "default=noprint_wrappers=1:nokey=1", source,
        ])
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.probes[key] = proc

        def done(*_args):
            text = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="replace").strip().splitlines()
            codec = text[0].strip().lower() if text else ""
            pixfmt = text[1].strip().lower() if len(text) > 1 else ""
            suffix = Path(source).suffix.lower()
            risky = (
                codec not in {"h264", "avc1"}
                or any(bit in pixfmt for bit in ("10le", "12le", "p010", "p016"))
                or suffix not in {".mp4", ".m4v", ".mov"}
                or key in self.forced
            )
            self.probes.pop(key, None)
            proc.deleteLater()
            if risky:
                self._start_proxy(index, key, source, proxy)

        proc.finished.connect(done)
        proc.start()

    def _start_proxy(self, index: int, key: str, source: str, proxy: Path) -> None:
        if key in self.transcodes:
            return
        ffmpeg = Path(self.editor.ffmpeg_exe)
        if not ffmpeg.is_file():
            return
        proxy.parent.mkdir(parents=True, exist_ok=True)
        proxy.unlink(missing_ok=True)
        proc = QProcess(self.page)
        proc.setProgram(str(ffmpeg))
        proc.setArguments([
            "-y", "-hide_banner", "-loglevel", "error", "-i", source,
            "-map", "0:v:0", "-map", "0:a:0?",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", str(proxy),
        ])
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.transcodes[key] = proc
        try:
            self.editor.status.setText(f"Preparando prévia compatível: {Path(source).name}…")
        except Exception:
            pass

        def done(exit_code: int, _status) -> None:
            self.transcodes.pop(key, None)
            ok = exit_code == 0 and proxy.is_file() and proxy.stat().st_size > 1024
            if ok:
                for clip in self.editor.clips:
                    if str(clip.get("path", "")) == source:
                        clip["_preview_path"] = str(proxy)
                current_idx = self._current_index()
                if current_idx >= 0 and str(self.editor.clips[current_idx].get("path", "")) == source:
                    self.editor.status.setText("Prévia compatível pronta. O original continua preservado para edição/exportação.")
                    self.editor.seek_sequence(self.editor.global_playhead_ms, self.editor.sequence_playing)
            else:
                detail = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
                if detail:
                    self.editor.status.setText(f"Não foi possível preparar a prévia compatível: {detail[-400:]}")
            proc.deleteLater()

        proc.finished.connect(done)
        proc.start()

    def _media_status_changed(self, status) -> None:
        try:
            from PySide6.QtMultimedia import QMediaPlayer
            if status not in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
                return
            idx = self._current_index()
            if idx >= 0:
                QTimer.singleShot(180, lambda i=idx: self._verify_video_track(i))
        except Exception:
            pass

    def _verify_video_track(self, index: int) -> None:
        if not (0 <= index < len(self.editor.clips)):
            return
        clip = self.editor.clips[index]
        if clip.get("_preview_path"):
            return
        try:
            tracks = self.editor.player.videoTracks()
        except Exception:
            tracks = [1]
        info = clip.get("info") or {}
        if not tracks and (int(info.get("width") or 0) > 0 or int(info.get("height") or 0) > 0):
            self.prepare(index, force=True)

    def force_current(self) -> None:
        idx = self._current_index()
        if idx >= 0:
            self.prepare(idx, force=True)

    def shutdown(self) -> None:
        for proc in [*self.probes.values(), *self.transcodes.values()]:
            _kill_process_tree(proc)
        self.probes.clear()
        self.transcodes.clear()


def _patch_video_preview() -> None:
    from monitor_noticias.ui.integrated_tools import OriginalVideoEditorPage

    if getattr(OriginalVideoEditorPage, "_v009_preview_patched", False):
        return
    original_init = OriginalVideoEditorPage.__init__
    original_shutdown = OriginalVideoEditorPage.shutdown

    def init(self, app_root):
        original_init(self, app_root)
        editor = getattr(self, "editor", None)
        if editor is not None:
            self._v009_preview_compat = _PreviewCompatController(self, editor)

    def shutdown(self) -> bool:
        compat = getattr(self, "_v009_preview_compat", None)
        if compat is not None:
            compat.shutdown()
        return original_shutdown(self)

    OriginalVideoEditorPage.__init__ = init
    OriginalVideoEditorPage.shutdown = shutdown
    OriginalVideoEditorPage._v009_preview_patched = True


def install_v009_runtime_fixes() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    _patch_sidebar()
    _patch_native_host_dpi()
    _patch_extractor_isolation()
    _patch_video_preview()
