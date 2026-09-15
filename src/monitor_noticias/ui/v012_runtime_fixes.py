from __future__ import annotations

"""Correções pontuais v0.0.12.

Mantém os motores originais e corrige apenas falhas observadas na integração:
- normalização final da barra lateral após os overlays v0.0.10/v0.0.11;
- continuidade de reprodução ao trocar a fonte do próximo clipe;
- download repetido do mesmo vídeo com nome incremental sem sobrescrever;
- resolução mais tolerante da capa atual do Washington Post no FrontPages.
"""

from pathlib import Path
import shutil
import tempfile

_INSTALLED = False


def _unique_parenthesized(path: Path) -> Path:
    """Retorna nome livre no padrão arquivo(1).ext, arquivo(2).ext..."""
    if not path.exists():
        return path
    for number in range(1, 10000):
        candidate = path.with_name(f"{path.stem}({number}){path.suffix}")
        if not candidate.exists():
            return candidate
    return path.with_name(f"{path.stem}(novo){path.suffix}")


def _install_extractor_repeat_download() -> None:
    """Executa yt-dlp em diretório temporário e só então move para Videos.

    Assim um arquivo já existente nunca faz o yt-dlp pular o download. O motor,
    seleção de formatos, autenticação e fallbacks continuam sendo os originais.
    """
    import re
    from monitor_noticias.extractor.core import ExtractorEngine

    if getattr(ExtractorEngine, "_v012_repeat_download", False):
        return
    ExtractorEngine._v012_repeat_download = True

    original = ExtractorEngine._run_ytdlp

    def run_ytdlp(self, url, selector, proxy, extra, update, executable=None, cookie_file=None, referer=None):
        executable = executable or self.yt_dlp
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix="monitor-download-"))
        cmd = [
            str(executable), "--no-playlist", "--newline", "--progress", "--windows-filenames",
            "--trim-filenames", "180", "--continue", "--retries", "10", "--fragment-retries", "10",
            "--retry-sleep", "http:linear=1::3", "--retry-sleep", "fragment:linear=1::3",
            "--socket-timeout", "30", "--ffmpeg-location", str(self.bin_dir),
            "-f", selector, "--merge-output-format", "mp4", "--remux-video", "mp4",
            "-o", str(temp_dir / "%(title).150B [%(id)s].%(ext)s"),
            "--print", "after_move:FINAL_FILE:%(filepath)s",
        ]
        self._common_runtime(cmd, proxy)
        if cookie_file is not None and cookie_file.exists():
            cmd += ["--cookies", str(cookie_file)]
        if referer:
            cmd += ["--referer", referer]
        cmd += extra
        cmd.append(url)
        proc = self.runner.start(cmd, directory=self.app_root)
        self._set_active(proc)
        final_path = ""
        tail = ""
        try:
            assert proc.stdout is not None
            for raw in proc.stdout:
                self._check_cancelled()
                line = raw.rstrip("\r\n")
                tail = (tail + "\n" + line)[-6000:]
                if line.startswith("FINAL_FILE:"):
                    final_path = line.split("FINAL_FILE:", 1)[1].strip().strip('"')
                match = re.search(r"(\d{1,3}(?:\.\d+)?)%", line)
                if match:
                    update(max(0, min(99, int(float(match.group(1))))), line[-220:])
                elif "[download]" in line or "[Merger]" in line or "[ffmpeg]" in line.lower():
                    update(0, line[-220:])
            code = proc.wait()
            if code != 0:
                raise RuntimeError(self._friendly_error(tail))

            final = Path(final_path) if final_path else None
            if final is None or not final.exists() or final.stat().st_size <= 1024:
                candidates = [p for p in temp_dir.iterdir() if p.is_file() and p.stat().st_size > 1024]
                final = max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None
            if final is None:
                raise RuntimeError("O processo terminou, mas nenhum arquivo de vídeo válido foi criado.")

            destination = _unique_parenthesized(self.videos_dir / final.name)
            shutil.move(str(final), str(destination))
            update(100, f"Download concluído: {destination.name}")
            return destination
        finally:
            self._clear_active(proc)
            shutil.rmtree(temp_dir, ignore_errors=True)

    run_ytdlp._v012_original = original
    ExtractorEngine._run_ytdlp = run_ytdlp


def _install_video_continuity() -> None:
    """Preserva a intenção de PLAY enquanto QMediaPlayer troca de arquivo."""
    from PySide6.QtCore import QTimer
    from PySide6.QtMultimedia import QMediaPlayer
    from monitor_noticias.ui.integrated_tools import OriginalVideoEditorPage

    if getattr(OriginalVideoEditorPage, "_v012_continuity", False):
        return
    OriginalVideoEditorPage._v012_continuity = True
    previous_init = OriginalVideoEditorPage.__init__

    def init(self, app_root):
        previous_init(self, app_root)
        editor = getattr(self, "editor", None)
        if editor is None or getattr(editor, "_v012_continuity_installed", False):
            return
        editor._v012_continuity_installed = True
        editor._v012_resume_requested = False

        original_seek = editor.seek_sequence

        def seek_sequence(global_ms, keep_playing=False):
            if keep_playing:
                editor._v012_resume_requested = True
            result = original_seek(global_ms, keep_playing)
            if keep_playing:
                for delay in (0, 80, 180, 360):
                    QTimer.singleShot(delay, lambda: _resume_if_requested(editor))
            return result

        editor.seek_sequence = seek_sequence

        def media_status(status):
            if status in (
                QMediaPlayer.MediaStatus.LoadedMedia,
                QMediaPlayer.MediaStatus.BufferedMedia,
                QMediaPlayer.MediaStatus.BufferingMedia,
            ):
                QTimer.singleShot(0, lambda: _resume_if_requested(editor))
            elif status == QMediaPlayer.MediaStatus.EndOfMedia:
                idx = int(getattr(editor, "preview_clip_index", -1))
                clips = getattr(editor, "clips", [])
                if 0 <= idx < len(clips) - 1:
                    editor._v012_resume_requested = True
                    boundary = sum(
                        max(0, int(c.get("end_ms", 0)) - int(c.get("start_ms", 0)))
                        for c in clips[: idx + 1]
                    )
                    QTimer.singleShot(0, lambda: editor.seek_sequence(boundary, True))

        def state_changed(state):
            if state == QMediaPlayer.PlaybackState.PlayingState:
                editor._v012_resume_requested = bool(getattr(editor, "sequence_playing", True))

        editor.player.mediaStatusChanged.connect(media_status)
        editor.player.playbackStateChanged.connect(state_changed)

    def _resume_if_requested(editor):
        if not getattr(editor, "_v012_resume_requested", False):
            return
        clips = getattr(editor, "clips", [])
        idx = int(getattr(editor, "preview_clip_index", -1))
        if not clips or not (0 <= idx < len(clips)):
            return
        status = editor.player.mediaStatus()
        if status in (QMediaPlayer.MediaStatus.NoMedia, QMediaPlayer.MediaStatus.InvalidMedia):
            return
        editor.sequence_playing = True
        editor.player.play()
        try:
            editor.btn_play.setText("Ⅱ  PAUSAR")
        except Exception:
            pass

    OriginalVideoEditorPage.__init__ = init


def _install_covers_frontpages_fix() -> None:
    """Amplia somente a descoberta da imagem atual do FrontPages."""
    from monitor_noticias.ui.integrated_tools import CoversPage

    if getattr(CoversPage, "_v012_frontpages", False):
        return
    CoversPage._v012_frontpages = True
    original_load_vendor = CoversPage._load_vendor

    def load_vendor(self, source_dir):
        ui_mod = original_load_vendor(self, source_dir)
        try:
            import importlib
            pkg = ui_mod.__package__
            resolver_mod = importlib.import_module(f"{pkg}.web_resolver")
            if not getattr(resolver_mod, "_v012_frontpages_js", False):
                resolver_mod._v012_frontpages_js = True
                resolver_mod.CURRENT_WEBP_JS = r"""
(function(slug){
 function clean(u){try{return new URL(String(u||'').replace(/&amp;/g,'&'),document.baseURI).href}catch(e){return String(u||'')}}
 function good(u){
   u=clean(u); var l=u.toLowerCase();
   if(!u || !/^https?:/i.test(u)) return '';
   if(slug==='the-washington-post' && l.indexOf('sports')>=0) return '';
   var ext=/\.(webp|jpe?g|png)(?:[?#]|$)/i.test(l);
   if(!ext) return '';
   var slugHit=l.indexOf(slug)>=0 || (slug==='the-washington-post' && (l.indexOf('washington-post')>=0 || l.indexOf('washingtonpost')>=0));
   return slugHit ? u : '';
 }
 var metas=document.querySelectorAll('meta[property="og:image"],meta[name="twitter:image"],meta[property="twitter:image"]');
 for(var m=0;m<metas.length;m++){var v=good(metas[m].content);if(v)return v}
 try{var rr=performance.getEntriesByType('resource')||[];for(var i=0;i<rr.length;i++){var v=good(rr[i].name);if(v)return v}}catch(e){}
 var imgs=[].slice.call(document.images||[]);
 var candidates=[];
 for(var j=0;j<imgs.length;j++){
   var im=imgs[j], vals=[im.currentSrc,im.src,im.getAttribute('data-src'),im.getAttribute('data-lazy-src'),im.getAttribute('data-original'),im.getAttribute('data-image'),im.getAttribute('data-full')];
   var sets=[im.getAttribute('srcset')||'',im.getAttribute('data-srcset')||''];
   for(var s=0;s<sets.length;s++){sets[s].split(',').forEach(function(x){vals.push(x.trim().split(/\s+/)[0])})}
   for(var q=0;q<vals.length;q++){
     var u=good(vals[q]); if(!u)continue;
     var w=im.naturalWidth||Number(im.getAttribute('width'))||0, h=im.naturalHeight||Number(im.getAttribute('height'))||0;
     var score=(w*h)+(h>w?5000000:0); candidates.push({u:u,score:score});
   }
 }
 candidates.sort(function(a,b){return b.score-a.score});
 if(candidates.length)return candidates[0].u;
 try{
   var html=document.documentElement?document.documentElement.innerHTML:'';
   var rx=/https?:[^'\"<>\s]+\.(?:webp|jpe?g|png)(?:\?[^'\"<>\s]*)?/ig, match;
   while((match=rx.exec(html))){var u=good(match[0].replace(/\\\//g,'/'));if(u)return u}
 }catch(e){}
 return '';
})(%SLUG%)
"""
        except Exception:
            pass
        return ui_mod

    CoversPage._load_vendor = load_vendor


def _install_sidebar_finalizer() -> None:
    from PySide6.QtCore import QByteArray, QSize, Qt
    from PySide6.QtGui import QIcon, QPainter, QPixmap
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout
    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section

    if getattr(MainWindow, "_v012_sidebar", False):
        return
    MainWindow._v012_sidebar = True

    svg = {
        Section.HOME: '<path d="M4 11L12 4l8 7v9h-6v-6h-4v6H4z"/>',
        Section.NEWS: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h6"/>',
        Section.VIDEOS: '<path d="M8 5l11 7-11 7z"/>',
        Section.DEMANDS: '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M4 8l8 6 8-6"/>',
        Section.SOURCES: '<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v7c0 2 3 3 7 3s7-1 7-3V5M5 12v7c0 2 3 3 7 3s7-1 7-3v-7"/>',
        Section.HISTORY: '<circle cx="12" cy="12" r="8"/><path d="M12 7v5l-4 2M5 5L3 9l4 1"/>',
        Section.TERMS: '<circle cx="10" cy="10" r="6"/><path d="M15 15l6 6"/>',
        Section.STOP: '<rect x="6" y="6" width="12" height="12" rx="1" fill="#eef7ff" stroke="none"/>',
        Section.PDF_EDITOR: '<path d="M6 3h8l4 4v14H6zM14 3v5h5"/><path d="M8 16c3-1 4-4 5-7 1 4 2 6 4 7-3-1-6-1-9 0"/>',
        Section.EXTRACTOR: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 5v14M17 5v14M3 9h4M17 9h4M3 15h4M17 15h4"/>',
        Section.VIDEO_EDITOR: '<path d="M4 8h16v12H4zM4 8l2-5h16l-2 5zM8 3L6 8M14 3l-2 5M20 3l-2 5"/>',
        Section.NEWS_EXTRACTOR: '<path d="M12 2c1 6 4 9 10 10-6 1-9 4-10 10-1-6-4-9-10-10 6-1 9-4 10-10z"/>',
        Section.SHEET_AUTOMATION: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M4 9h16M10 9v12M4 15h16"/>',
        Section.COVERS: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="9" r="2"/><path d="M5 18l5-5 3 3 2-2 4 4"/>',
        Section.SETTINGS: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    }

    def make_icon(section):
        body = svg.get(section, '')
        xml = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="#eef7ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
        pix = QPixmap(28, 28)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        QSvgRenderer(QByteArray(xml.encode("utf-8"))).render(painter)
        painter.end()
        return QIcon(pix)

    def group_header(text):
        frame = QFrame()
        frame.setObjectName("sideGroupHeader")
        row = QHBoxLayout(frame)
        row.setContentsMargins(1, 8, 0, 5)
        row.setSpacing(8)
        dash = QLabel("━")
        dash.setObjectName("sideGroupDash")
        dash.setFixedWidth(28)
        title = QLabel(text)
        title.setObjectName("sideGroupTitle")
        row.addWidget(dash)
        row.addWidget(title, 1)
        return frame

    def normalize(self):
        sidebar = getattr(self, "sidebar", None)
        if sidebar is None:
            return
        sidebar.setFixedWidth(318)

        for holder in self.nav_holders.values():
            holder_layout = holder.layout()
            if holder_layout is None:
                continue
            holder.setFixedHeight(58)
            for label in holder.findChildren(QLabel, "", Qt.FindChildOption.FindDirectChildrenOnly):
                if label.text().strip() == "●" and "border-left" in label.styleSheet():
                    holder_layout.removeWidget(label)
                    label.hide()
                    label.setParent(None)
                    label.deleteLater()

        news_button = self.nav_buttons.get(Section.NEWS)
        badge = getattr(self, "news_badge", None)
        if news_button is not None and badge is not None:
            old_layout = self.nav_holders[Section.NEWS].layout()
            if old_layout is not None:
                old_layout.removeWidget(badge)
            badge.setParent(news_button)
            badge.show()
            badge.raise_()
            badge.setFixedWidth(31)
            badge.move(max(0, news_button.width() - 39), 17)

        for section, button in self.nav_buttons.items():
            button.setIcon(make_icon(section))
            button.setIconSize(QSize(28, 28))
            button.setText(section.value.label)
            button.setMinimumHeight(54)
            button.setMaximumHeight(54)
            button.setStyleSheet("padding-left:18px; text-align:left;")

        scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
        content = scroll.widget() if scroll is not None else None
        layout = content.layout() if content is not None else None
        if isinstance(layout, QVBoxLayout):
            # setParent(None) retira imediatamente os cabeçalhos antigos da árvore
            # QObject. deleteLater sozinho só os removeria no próximo event loop e
            # causava multiplicação ao navegar rapidamente entre abas.
            for frame in content.findChildren(QFrame, "sideGroupHeader"):
                layout.removeWidget(frame)
                frame.hide()
                frame.setParent(None)
                frame.deleteLater()
            for title, first in reversed((
                ("PRINCIPAL", Section.HOME),
                ("GERENCIAMENTO", Section.DEMANDS),
                ("FERRAMENTAS", Section.PDF_EDITOR),
                ("SISTEMA", Section.SETTINGS),
            )):
                holder = self.nav_holders[first]
                index = layout.indexOf(holder)
                if index >= 0:
                    layout.insertWidget(index, group_header(title))

        current = getattr(self, "_current", Section.HOME)
        for section, button in self.nav_buttons.items():
            button.setChecked(section == current)
            if section == current:
                button.setText(section.value.label + "   ❯")
        if news_button is not None and badge is not None:
            badge.move(max(0, news_button.width() - 39), 17)

    previous_build = MainWindow._build_ui
    previous_navigate = MainWindow.navigate

    def build(self):
        previous_build(self)
        normalize(self)

    def navigate(self, section):
        previous_navigate(self, section)
        normalize(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate


def install_v012_runtime_fixes() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    _install_extractor_repeat_download()
    _install_video_continuity()
    _install_covers_frontpages_fix()
    _install_sidebar_finalizer()
