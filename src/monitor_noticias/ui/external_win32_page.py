from __future__ import annotations

import logging
import os
from pathlib import Path
import subprocess
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

log = logging.getLogger(__name__)


class _NativeHost(QWidget):
    """Área nativa que recebe uma janela Win32 filha sem modificar o app externo."""

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors, True)
        self.setMinimumSize(520, 360)
        self._child_hwnd = 0

    def attach(self, hwnd: int) -> None:
        self._child_hwnd = int(hwnd or 0)
        self._resize_child()

    def detach(self) -> None:
        self._child_hwnd = 0

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._resize_child()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._resize_child()

    def _resize_child(self) -> None:
        if os.name != "nt" or not self._child_hwnd:
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            if user32.IsWindow(self._child_hwnd):
                user32.SetWindowPos(
                    self._child_hwnd, 0, 0, 0,
                    max(1, self.width()), max(1, self.height()),
                    0x0004 | 0x0010 | 0x0040,
                )
        except Exception:
            log.exception("Falha ao redimensionar janela externa incorporada")


class ExternalWin32AppPage(QWidget):
    """Hospeda um programa Windows original em processo isolado dentro do Monitor.

    O executável externo continua sendo o aplicativo original, com seus próprios
    arquivos, motor, IPC, persistência e dependências. O Monitor só cria o processo
    e reparenta a janela Win32 para esta área visual. Se o processo externo falhar,
    o Monitor permanece aberto.
    """

    def __init__(
        self,
        app_root: Path,
        *,
        title: str,
        executable_relpath: str,
        description: str,
        expected_window_title: str = "",
    ) -> None:
        super().__init__()
        self.app_root = Path(app_root)
        self.title = title
        self.description = description
        self.executable = self.app_root / "resources" / "integrations" / executable_relpath
        self.expected_window_title = expected_window_title.casefold().strip()
        self._process: subprocess.Popen[object] | None = None
        self._hwnd = 0
        self._launch_started_at = 0.0
        self._closing = False

        self._build_ui()
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(250)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_timer.start()
        QTimer.singleShot(350, self.start)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        bar = QFrame()
        bar.setObjectName("filterCard")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 8, 14, 8)
        text = QVBoxLayout()
        text.setSpacing(1)
        title = QLabel(self.title)
        title.setObjectName("sectionTitle")
        subtitle = QLabel(self.description)
        subtitle.setObjectName("smallText")
        subtitle.setWordWrap(True)
        text.addWidget(title)
        text.addWidget(subtitle)
        layout.addLayout(text, 1)
        self.status = QLabel("Preparando integração...")
        self.status.setObjectName("smallText")
        layout.addWidget(self.status)
        self.restart_button = QPushButton("Reabrir")
        self.restart_button.setProperty("secondary", True)
        self.restart_button.clicked.connect(self.restart)
        self.restart_button.setVisible(False)
        layout.addWidget(self.restart_button)
        root.addWidget(bar)

        self.host = _NativeHost()
        self.host.setStyleSheet("background:#020b16;border:1px solid #0a6f9c;border-radius:10px;")
        root.addWidget(self.host, 1)

    def refresh(self, _state=None) -> None:
        pass

    def start(self) -> None:
        if self._closing or self._process is not None:
            return
        if os.environ.get("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS") == "1":
            self.status.setText("Integração externa desativada no ambiente de teste.")
            self.restart_button.setVisible(False)
            return
        if os.name != "nt":
            self.status.setText("Integração disponível somente no Windows.")
            self.restart_button.setVisible(False)
            return
        if not self.executable.is_file():
            self.status.setText(f"Executável não encontrado: {self.executable.name}")
            self.restart_button.setVisible(True)
            return
        try:
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            self._process = subprocess.Popen(
                [str(self.executable)],
                cwd=str(self.executable.parent),
                shell=False,
                creationflags=creationflags,
            )
            self._launch_started_at = time.monotonic()
            self.status.setText("Abrindo aplicativo original...")
            self.restart_button.setVisible(False)
        except Exception as exc:
            log.exception("Não foi possível iniciar %s", self.title)
            self._process = None
            self.status.setText(f"Falha ao abrir: {exc}")
            self.restart_button.setVisible(True)

    def restart(self) -> None:
        self._stop_external(force=True)
        QTimer.singleShot(250, self.start)

    def _poll(self) -> None:
        process = self._process
        if process is None:
            return
        code = process.poll()
        if code is not None:
            self._process = None
            self._hwnd = 0
            self.host.detach()
            if not self._closing:
                self.status.setText(f"Aplicativo encerrou (código {code}). O Monitor continua aberto.")
                self.restart_button.setVisible(True)
            return

        if self._hwnd and self._is_window(self._hwnd):
            return

        hwnd = self._find_window_for_pid(process.pid)
        if hwnd:
            try:
                self._embed_window(hwnd)
                self._hwnd = hwnd
                self.host.attach(hwnd)
                self.status.setText("Integrado e em execução")
                self.restart_button.setVisible(False)
            except Exception as exc:
                log.exception("Falha ao incorporar janela de %s", self.title)
                self.status.setText(f"Aplicativo aberto, mas a janela não pôde ser incorporada: {exc}")
        elif self._launch_started_at and time.monotonic() - self._launch_started_at > 30:
            self.status.setText("Aplicativo em execução; aguardando a janela principal...")

    @staticmethod
    def _is_window(hwnd: int) -> bool:
        if os.name != "nt":
            return False
        try:
            import ctypes
            return bool(ctypes.windll.user32.IsWindow(int(hwnd)))
        except Exception:
            return False

    def _find_window_for_pid(self, pid: int) -> int:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        matches: list[tuple[int, str]] = []
        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        @callback_type
        def enum_proc(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            proc_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
            if int(proc_id.value) != int(pid):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(max(1, length + 1))
            user32.GetWindowTextW(hwnd, buf, len(buf))
            title = buf.value or ""
            matches.append((int(hwnd), title))
            return True

        user32.EnumWindows(enum_proc, 0)
        if not matches:
            return 0
        if self.expected_window_title:
            for hwnd, title in matches:
                if self.expected_window_title in title.casefold():
                    return hwnd
        for hwnd, title in matches:
            if title.strip():
                return hwnd
        return matches[0][0]

    def _embed_window(self, hwnd: int) -> None:
        import ctypes

        user32 = ctypes.windll.user32
        GWL_STYLE = -16
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        WS_POPUP = 0x80000000
        WS_CHILD = 0x40000000
        WS_VISIBLE = 0x10000000
        SWP_FRAMECHANGED = 0x0020
        SWP_SHOWWINDOW = 0x0040
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010

        parent = int(self.host.winId())
        user32.SetParent(int(hwnd), parent)
        style = int(user32.GetWindowLongW(int(hwnd), GWL_STYLE))
        style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU | WS_POPUP)
        style |= WS_CHILD | WS_VISIBLE
        user32.SetWindowLongW(int(hwnd), GWL_STYLE, style)
        user32.SetWindowPos(
            int(hwnd), 0, 0, 0,
            max(1, self.host.width()), max(1, self.host.height()),
            SWP_FRAMECHANGED | SWP_SHOWWINDOW | SWP_NOZORDER | SWP_NOACTIVATE,
        )

    def _stop_external(self, *, force: bool) -> None:
        process = self._process
        if process is None:
            return
        try:
            if self._hwnd and self._is_window(self._hwnd):
                import ctypes
                ctypes.windll.user32.PostMessageW(int(self._hwnd), 0x0010, 0, 0)
            try:
                process.wait(timeout=2.5)
            except subprocess.TimeoutExpired:
                if force and os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                    try:
                        process.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        pass
        except Exception:
            log.exception("Falha ao encerrar integração %s", self.title)
        finally:
            self._process = None
            self._hwnd = 0
            self.host.detach()

    def shutdown(self) -> bool:
        self._closing = True
        self._poll_timer.stop()
        self._stop_external(force=True)
        return True
