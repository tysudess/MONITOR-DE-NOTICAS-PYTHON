from __future__ import annotations


def install_v010_video_boundary_fix() -> None:
    from PySide6.QtCore import QTimer
    from PySide6.QtMultimedia import QMediaPlayer
    from monitor_noticias.ui.integrated_tools import OriginalVideoEditorPage

    if getattr(OriginalVideoEditorPage, "_v010_eos_boundary_patched", False):
        return

    previous_init = OriginalVideoEditorPage.__init__

    def init(self, app_root):
        previous_init(self, app_root)
        editor = getattr(self, "editor", None)
        if editor is None or getattr(editor, "_v010_eos_boundary_installed", False):
            return
        editor._v010_eos_boundary_installed = True
        editor._v010_eos_transitioning = False

        def continue_after_eos(*_args):
            if editor._v010_eos_transitioning:
                return
            idx = int(getattr(editor, "preview_clip_index", -1))
            clips = getattr(editor, "clips", [])
            if not (0 <= idx < len(clips) - 1):
                return
            # O editor original marca sequence_playing=False ao receber
            # EndOfMedia. Reativamos somente quando ainda existe próximo clipe.
            if editor.player.mediaStatus() != QMediaPlayer.MediaStatus.EndOfMedia:
                return
            editor._v010_eos_transitioning = True
            boundary = sum(
                max(0, int(c.get("end_ms", 0)) - int(c.get("start_ms", 0)))
                for c in clips[: idx + 1]
            )

            def switch():
                try:
                    editor.sequence_playing = True
                    editor.seek_sequence(boundary, True)
                finally:
                    QTimer.singleShot(450, lambda: setattr(editor, "_v010_eos_transitioning", False))

            QTimer.singleShot(0, switch)

        editor.player.mediaStatusChanged.connect(
            lambda status: continue_after_eos() if status == QMediaPlayer.MediaStatus.EndOfMedia else None
        )
        editor.player.playbackStateChanged.connect(
            lambda state: continue_after_eos() if state == QMediaPlayer.PlaybackState.StoppedState else None
        )

    OriginalVideoEditorPage.__init__ = init
    OriginalVideoEditorPage._v010_eos_boundary_patched = True
