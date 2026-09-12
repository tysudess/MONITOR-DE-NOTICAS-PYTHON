from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QObject, QPoint, QRect, QRunnable, QThread, QThreadPool, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QDragEnterEvent, QDropEvent, QImage, QKeySequence, QMouseEvent, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QFileDialog, QFrame, QHBoxLayout, QInputDialog,
    QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QScrollArea,
    QSizePolicy, QSplitter, QStackedWidget, QVBoxLayout, QWidget,
)

from monitor_noticias.pdf_editor import PdfCrop, PdfEditorModel, PdfExportQuality, SUPPORTED_IMPORTS

log = logging.getLogger(__name__)


def _pil_to_qimage(image: Image.Image) -> QImage:
    rgb = image.convert("RGB")
    return QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format.Format_RGB888).copy()


class _ImageWorker(QObject):
    done = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, token: int, fn) -> None:
        super().__init__(); self.token = token; self.fn = fn

    def run(self) -> None:
        try: self.done.emit(self.token, _pil_to_qimage(self.fn()))
        except Exception as exc: self.failed.emit(self.token, str(exc))


class _ExportWorker(QObject):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, model: PdfEditorModel, output: Path, include_cover: bool) -> None:
        super().__init__(); self.model=model; self.output=output; self.include_cover=include_cover

    def run(self) -> None:
        try:
            path = self.model.export_pdf(self.output, include_cover=self.include_cover, quality=PdfExportQuality.HIGH)
            self.done.emit(str(path))
        except Exception as exc: self.failed.emit(str(exc))


class _ThumbSignals(QObject):
    ready = Signal(str, object)


class _ThumbTask(QRunnable):
    def __init__(self, model: PdfEditorModel, index: int, uid: str, signals: _ThumbSignals) -> None:
        super().__init__(); self.model=model; self.index=index; self.uid=uid; self.signals=signals

    def run(self) -> None:
        try: self.signals.ready.emit(self.uid, _pil_to_qimage(self.model.render_thumbnail(self.index)))
        except Exception: log.exception("Falha ao gerar miniatura PDF")


class PdfPreview(QWidget):
    crop_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(); self.setMinimumSize(620, 520); self.setMouseTracking(True)
        self._image: QImage | None = None; self._zoom=1.0; self._image_rect=QRect(); self._crop_mode=False
        self._start: QPoint | None=None; self._end: QPoint | None=None; self._existing: PdfCrop | None=None

    def set_image(self, image: QImage | None, zoom: float, existing_crop: PdfCrop | None = None) -> None:
        self._image=image; self._zoom=zoom; self._existing=existing_crop; self._start=None; self._end=None; self.update()

    def begin_crop(self, image: QImage, zoom: float, existing_crop: PdfCrop | None) -> None:
        self.set_image(image, zoom, existing_crop); self._crop_mode=True; self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, _event) -> None:
        from PySide6.QtGui import QPainter, QPen, QColor, QFont
        p=QPainter(self); p.fillRect(self.rect(), QColor(7,17,30)); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._image is None or self._image.isNull():
            cx=self.width()//2; cy=self.height()//2-20; p.setPen(QColor(214,164,77)); p.setFont(QFont("Sans Serif",20,QFont.Weight.Bold)); p.drawText(QRect(cx-280,cy-40,560,40),Qt.AlignmentFlag.AlignCenter,"Arraste e solte seus arquivos aqui")
            p.setPen(QColor(164,175,194)); p.setFont(QFont("Sans Serif",12)); p.drawText(QRect(cx-280,cy+8,560,30),Qt.AlignmentFlag.AlignCenter,"Suporte a PDFs e imagens (JPG, PNG, etc.)")
            return
        fit=min(max(1,self.width()-34)/self._image.width(),max(1,self.height()-34)/self._image.height())
        scale=max(.03,fit)*self._zoom; w=max(1,round(self._image.width()*scale)); h=max(1,round(self._image.height()*scale)); x=(self.width()-w)//2; y=(self.height()-h)//2
        self._image_rect=QRect(x,y,w,h); p.fillRect(x-1,y-1,w+2,h+2,Qt.GlobalColor.white); p.drawImage(self._image_rect,self._image)
        if self._existing is not None:
            c=self._existing; rx=x+round(c.x*w); ry=y+round(c.y*h); rw=max(1,round(c.w*w)); rh=max(1,round(c.h*h)); p.setPen(QPen(QColor(30,137,255),2)); p.drawRect(rx,ry,rw,rh)
        if self._start is not None and self._end is not None:
            rect=QRect(self._start,self._end).normalized(); p.fillRect(rect,QColor(30,137,255,55)); p.setPen(QPen(QColor(30,137,255),2)); p.drawRect(rect)

    def _clamp(self, point: QPoint) -> QPoint:
        r=self._image_rect
        return QPoint(min(max(point.x(),r.left()),r.right()),min(max(point.y(),r.top()),r.bottom()))

    def mousePressEvent(self,event:QMouseEvent)->None:
        if self._crop_mode and self._image_rect.contains(event.position().toPoint()): self._start=self._clamp(event.position().toPoint()); self._end=self._start; self.update()

    def mouseMoveEvent(self,event:QMouseEvent)->None:
        if self._crop_mode and self._start is not None: self._end=self._clamp(event.position().toPoint()); self.update()

    def mouseReleaseEvent(self,event:QMouseEvent)->None:
        if not self._crop_mode or self._start is None: return
        end=self._clamp(event.position().toPoint()); rect=QRect(self._start,end).normalized(); r=self._image_rect
        if rect.width()>4 and rect.height()>4 and r.width()>0 and r.height()>0:
            self.crop_selected.emit(PdfCrop((rect.left()-r.left())/r.width(),(rect.top()-r.top())/r.height(),rect.width()/r.width(),rect.height()/r.height()))
        self._crop_mode=False; self.unsetCursor(); self._start=None; self._end=None; self.update()


class ReorderList(QListWidget):
    reorder_requested = Signal(int,int)

    def __init__(self) -> None:
        super().__init__(); self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection); self.setDragEnabled(True); self.setAcceptDrops(True); self.setDropIndicatorShown(True); self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dropEvent(self,event:QDropEvent)->None:
        source=self.currentRow(); point=event.position().toPoint(); target=self.indexAt(point).row()
        if target<0: target=self.count()
        else:
            rect=self.visualItemRect(self.item(target))
            if point.y()>rect.center().y(): target+=1
        event.ignore(); self.reorder_requested.emit(source,target)


class PdfEditorPage(QWidget):
    back_requested = Signal()

    def __init__(self, app_root: Path) -> None:
        super().__init__(); self.model=PdfEditorModel(app_root); self.setAcceptDrops(True); self._preview_token=0; self._preview_thread:QThread|None=None; self._export_thread:QThread|None=None; self._thumb_signals=_ThumbSignals(); self._thumb_signals.ready.connect(self._thumbnail_ready); self._pool=QThreadPool.globalInstance(); self._build(); self._shortcuts(); self._refresh_all()

    def _button(self,text:str,slot)->QPushButton:
        b=QPushButton(text); b.setMinimumHeight(38); b.clicked.connect(slot); return b

    def _build(self)->None:
        root=QVBoxLayout(self); root.setContentsMargins(8,6,8,6); root.setSpacing(8)
        header=QHBoxLayout(); brand=QVBoxLayout(); a=QLabel("DEPARTAMENTO\nDE IMPRENSA"); a.setStyleSheet("font-size:22px;font-weight:700;color:#d6a44d"); brand.addWidget(a); header.addLayout(brand); header.addStretch()
        center=QVBoxLayout(); title=QLabel("VISUALIZAÇÃO DO DOCUMENTO"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); title.setStyleSheet("font-size:22px;font-weight:700"); center.addWidget(title); sub=QLabel("Adicione uma imagem ou PDF para começar a editar"); sub.setAlignment(Qt.AlignmentFlag.AlignCenter); center.addWidget(sub); bank=QLabel("Banco de Opiniões 1304"); bank.setAlignment(Qt.AlignmentFlag.AlignCenter); bank.setObjectName("muted"); center.addWidget(bank); header.addLayout(center,2); header.addStretch(); back=self._button("←  Voltar ao Monitor",self.back_requested.emit); header.addWidget(back); root.addLayout(header)
        body=QHBoxLayout(); body.setSpacing(10)
        left=QFrame(); left.setFixedWidth(220); ll=QVBoxLayout(left); ll.setContentsMargins(8,4,8,8); ll.setSpacing(5)
        ll.addWidget(self._button("↑  Arquivos",self._choose_all)); ll.addWidget(self._button("PDF",self._choose_pdfs)); ll.addWidget(self._button("✂  Cortar",self._start_crop)); ll.addWidget(self._button("⛶  Redimensionar",self._resize_visual)); ll.addWidget(self._button("▤  Criar",self._create_blank)); ll.addWidget(self._button("▥  Excluir",self._delete)); ll.addWidget(self._button("↕  Ordenar",self._focus_reorder)); ll.addStretch(); drop=QLabel("☁\n\nArraste\nPDF/imagem\nou selecione"); drop.setAlignment(Qt.AlignmentFlag.AlignCenter); drop.setMinimumHeight(170); drop.setStyleSheet("border:1px dashed #d6a44d;border-radius:8px;color:#d7d5d0"); ll.addWidget(drop); ll.addWidget(self._button("Selecionar",self._choose_all)); body.addWidget(left)
        middle=QVBoxLayout(); controls=QHBoxLayout(); controls.addWidget(self._button("−",lambda:self._zoom(-.15))); self.zoom_label=QLabel("100%"); self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter); controls.addWidget(self.zoom_label); controls.addWidget(self._button("+",lambda:self._zoom(.15))); controls.addWidget(self._button("⛶  Ajustar",lambda:self._set_zoom(1.0))); controls.addSpacing(8); controls.addWidget(self._button("↶",self._undo)); controls.addWidget(self._button("↷",self._redo)); controls.addWidget(self._button("▱  Limpar",self._clear)); controls.addStretch(); self.thumb_mode=self._button("▦  Miniatural",lambda:self._set_list_mode(True)); self.list_mode=self._button("☷  Lista",lambda:self._set_list_mode(False)); controls.addWidget(self.thumb_mode); controls.addWidget(self.list_mode); self.page_count=QLabel("0 páginas"); controls.addWidget(self.page_count); middle.addLayout(controls)
        content=QHBoxLayout(); self.preview=PdfPreview(); self.preview.setStyleSheet("border:1px solid #4d6786"); self.preview.crop_selected.connect(self._crop_done); content.addWidget(self.preview,1); self.thumbs=ReorderList(); self.thumbs.setFixedWidth(92); self.thumbs.currentRowChanged.connect(self._select); self.thumbs.reorder_requested.connect(self._reorder); content.addWidget(self.thumbs); middle.addLayout(content,1); body.addLayout(middle,1)
        right=QFrame(); right.setFixedWidth(245); rl=QVBoxLayout(right); rl.setContentsMargins(10,10,10,10); title2=QLabel("Capa e Exportação"); title2.setStyleSheet("font-size:18px;font-weight:700"); rl.addWidget(title2); self.include_cover=QCheckBox("•  Incluir capa padrão"); self.include_cover.setChecked(True); rl.addWidget(self.include_cover); self.cover=QLabel(); self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter); self.cover.setMinimumHeight(230); self.cover.setStyleSheet("border:1px solid #d6a44d"); rl.addWidget(self.cover); rl.addWidget(self._button("▧  Trocar capa",self._change_cover)); rl.addStretch(); self.export_button=self._button("✔  GERAR PDF",self._export); self.export_button.setMinimumHeight(58); rl.addWidget(self.export_button); body.addWidget(right); root.addLayout(body,1)
        self.status=QLabel(""); self.status.setObjectName("muted"); root.addWidget(self.status)

    def _shortcuts(self)->None:
        for seq,slot in (("Ctrl+Z",self._undo),("Ctrl+Y",self._redo),("Delete",self._delete),("Ctrl+S",self._export)):
            QShortcut(QKeySequence(seq),self,activated=slot)

    def refresh(self,_state=None)->None: pass

    def _choose_all(self)->None:
        names,_=QFileDialog.getOpenFileNames(self,"Selecionar arquivos","","PDF e imagens (*.pdf *.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif)"); self._import([Path(x) for x in names])

    def _choose_pdfs(self)->None:
        names,_=QFileDialog.getOpenFileNames(self,"Selecionar PDFs","","Arquivos PDF (*.pdf)"); self._import([Path(x) for x in names])

    def _import(self,paths:list[Path])->None:
        if not paths:return
        errors=self.model.import_files(paths); self._refresh_all()
        for error in errors: QMessageBox.critical(self,"Editor de PDF",error)

    def dragEnterEvent(self,event:QDragEnterEvent)->None:
        if event.mimeData().hasUrls() and any(Path(u.toLocalFile()).suffix.lower() in SUPPORTED_IMPORTS for u in event.mimeData().urls()): event.acceptProposedAction()

    def dropEvent(self,event:QDropEvent)->None:
        self._import([Path(u.toLocalFile()) for u in event.mimeData().urls()]); event.acceptProposedAction()

    def _create_blank(self)->None: self.model.create_blank_page(); self._refresh_all()
    def _delete(self)->None:
        if self.model.delete_selected(): self._refresh_all()
    def _clear(self)->None:
        if not self.model.pages:return
        if QMessageBox.question(self,"Limpar","Remover todas as páginas do documento?")==QMessageBox.StandardButton.Yes: self.model.clear_all(); self._refresh_all()
    def _undo(self)->None:
        if self.model.undo(): self._refresh_all()
    def _redo(self)->None:
        if self.model.redo(): self._refresh_all()
    def _zoom(self,delta:float)->None:self._set_zoom(self.model.zoom+delta)
    def _set_zoom(self,value:float)->None:self.model.set_zoom(value); self.zoom_label.setText(f"{round(self.model.zoom*100)}%"); self._request_preview()

    def _resize_visual(self)->None:
        if self.model.selected_index not in range(len(self.model.pages)): QMessageBox.critical(self,"Editor de PDF","Selecione uma página para redimensionar."); return
        value,ok=QInputDialog.getItem(self,"Redimensionar","Escolha a escala de visualização da página:",["75%","90%","100%","110%","125%"],2,False)
        if ok:self._set_zoom(float(value.removesuffix("%"))/100.0)

    def _focus_reorder(self)->None: self.thumbs.setFocus(); QMessageBox.information(self,"Reordenar","Arraste as miniaturas na coluna lateral de páginas para mudar a ordem.")
    def _reorder(self,source:int,target:int)->None:
        if self.model.reorder(source,target): self._refresh_all()

    def _select(self,row:int)->None:
        if 0<=row<len(self.model.pages): self.model.selected_index=row
        elif not self.model.pages:self.model.selected_index=-1
        self._request_preview()

    def _start_crop(self)->None:
        idx=self.model.selected_index
        if idx not in range(len(self.model.pages)): QMessageBox.critical(self,"Editor de PDF","Selecione uma página para recortar."); return
        self._preview_token+=1; token=self._preview_token; page=self.model.pages[idx]
        self._run_image_worker(token,lambda:self.model.render_transformed_source(page,120),lambda image:self.preview.begin_crop(image,self.model.zoom,page.crop))

    def _crop_done(self,crop:PdfCrop)->None:
        if self.model.apply_crop(crop): self._refresh_all()

    def _run_image_worker(self,token:int,fn,on_done=None)->None:
        if self._preview_thread is not None and self._preview_thread.isRunning(): self._preview_token+=1
        thread=QThread(self); worker=_ImageWorker(token,fn); worker.moveToThread(thread); thread.started.connect(worker.run)
        def done(t:int,image:QImage):
            if t==self._preview_token:
                if on_done:on_done(image)
                else:self.preview.set_image(image,self.model.zoom,None)
            thread.quit()
        worker.done.connect(done); worker.failed.connect(lambda t,msg:(self.status.setText(msg) if t==self._preview_token else None,thread.quit())); thread.finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater); self._preview_thread=thread; self._preview_worker=worker; thread.start()

    def _request_preview(self)->None:
        idx=self.model.selected_index; self._preview_token+=1; token=self._preview_token
        if idx not in range(len(self.model.pages)): self.preview.set_image(None,self.model.zoom); return
        self._run_image_worker(token,lambda:self.model.render_preview(idx))

    def _set_list_mode(self,thumbs:bool)->None:
        self.thumbs.setIconSize(__import__("PySide6.QtCore",fromlist=["QSize"]).QSize(56,84) if thumbs else __import__("PySide6.QtCore",fromlist=["QSize"]).QSize(0,0))
        for i in range(self.thumbs.count()): self.thumbs.item(i).setSizeHint(__import__("PySide6.QtCore",fromlist=["QSize"]).QSize(80,108 if thumbs else 46))

    def _refresh_all(self)->None:
        selected=self.model.selected_index; self.thumbs.blockSignals(True); self.thumbs.clear()
        for index,page in enumerate(self.model.pages):
            item=QListWidgetItem(str(index+1)); item.setData(Qt.ItemDataRole.UserRole,page.uid); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.thumbs.addItem(item); self._pool.start(_ThumbTask(self.model,index,page.uid,self._thumb_signals))
        self.thumbs.setVisible(bool(self.model.pages)); self.page_count.setText(f"{len(self.model.pages)} {'página' if len(self.model.pages)==1 else 'páginas'}")
        if 0<=selected<self.thumbs.count(): self.thumbs.setCurrentRow(selected)
        self.thumbs.blockSignals(False); self.zoom_label.setText(f"{round(self.model.zoom*100)}%"); self._refresh_cover(); self._request_preview()

    def _thumbnail_ready(self,uid:str,image:QImage)->None:
        for i in range(self.thumbs.count()):
            item=self.thumbs.item(i)
            if item.data(Qt.ItemDataRole.UserRole)==uid: item.setIcon(QPixmap.fromImage(image)); item.setSizeHint(__import__("PySide6.QtCore",fromlist=["QSize"]).QSize(80,108)); break

    def _refresh_cover(self)->None:
        try:
            image=_pil_to_qimage(self.model.current_cover_image()); pix=QPixmap.fromImage(image).scaled(205,205,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation); self.cover.setPixmap(pix)
        except Exception as exc:self.status.setText(str(exc))

    def _change_cover(self)->None:
        name,_=QFileDialog.getOpenFileName(self,"Trocar capa","","Imagem (*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif)")
        if not name:return
        try:self.model.save_custom_cover(Path(name)); self._refresh_cover()
        except Exception as exc:QMessageBox.critical(self,"Editor de PDF",f"Não foi possível trocar a capa: {exc}")

    def _export(self)->None:
        if not self.model.pages and not self.include_cover.isChecked(): QMessageBox.critical(self,"Editor de PDF","Adicione ao menos uma página ou mantenha a capa ativada."); return
        default="RADAR DE NOTICIAS - MIDIA IMPRESSA.pdf" if self.include_cover.isChecked() else "documento.pdf"; name,_=QFileDialog.getSaveFileName(self,"Salvar PDF",default,"PDF (*.pdf)")
        if not name:return
        self.export_button.setEnabled(False); self.status.setText("Gerando PDF..."); thread=QThread(self); worker=_ExportWorker(self.model,Path(name),self.include_cover.isChecked()); worker.moveToThread(thread); thread.started.connect(worker.run)
        def success(path:str):
            self.export_button.setEnabled(True); self.status.setText(f"PDF gerado com sucesso: {path}"); box=QMessageBox(self); box.setWindowTitle("Exportação concluída"); box.setText(f"PDF gerado com sucesso!\n{path}"); ok=box.addButton("OK",QMessageBox.ButtonRole.AcceptRole); folder=box.addButton("Abrir pasta",QMessageBox.ButtonRole.ActionRole); box.exec();
            if box.clickedButton() is folder: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent))); thread.quit()
        def failure(msg:str):self.export_button.setEnabled(True); self.status.setText(msg); QMessageBox.critical(self,"Editor de PDF",f"Erro ao gerar PDF: {msg}"); thread.quit()
        worker.done.connect(success); worker.failed.connect(failure); thread.finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater); self._export_thread=thread; self._export_worker=worker; thread.start()
