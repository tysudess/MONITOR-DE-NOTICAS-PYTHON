from __future__ import annotations

"""Correções de estabilidade do Editor PDF da v0.0.11.

Motivação objetiva:
- a v0.0.10 ainda apontava o fallback HD para um WebP truncado;
- preview em QThread + miniaturas em QThreadPool podiam renderizar o mesmo PDF
  simultaneamente via PDFium. A UI do editor passa a serializar renderização no
  thread da interface. É mais conservador, porém elimina corrida nativa/Qt que
  pode encerrar o processo inteiro.

O motor de importação/exportação e as regras do documento permanecem no
PdfEditorModel original. Esta camada apenas torna a chamada da UI segura.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox

log = logging.getLogger(__name__)
_INSTALLED = False


def install_v011_pdf_stability() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.pdf_editor import PdfEditorModel, PdfExportQuality
    from monitor_noticias.ui.pdf_editor_page import PdfEditorPage, _pil_to_qimage

    # O PNG de 1245x2048 é o asset oficial e íntegro. O .b64 continua como
    # fallback de portabilidade do motor; o WebP truncado da v0.0.9 não é usado.
    original_model_init = PdfEditorModel.__init__

    def model_init(self, app_root):
        original_model_init(self, app_root)
        png = Path(app_root) / "resources" / "pdf-default-cover.png"
        if png.is_file():
            self.hd_default_cover_file = png

    PdfEditorModel.__init__ = model_init

    def report_error(self, context: str, exc: BaseException) -> None:
        log.exception("Editor PDF: %s", context, exc_info=(type(exc), exc, exc.__traceback__))
        message = f"{context}: {exc}"
        try:
            self.status.setText(message)
            QMessageBox.critical(self, "Editor de PDF", message)
        except Exception:
            log.exception("Falha ao apresentar erro isolado do Editor PDF")

    def safe_import(self, paths):
        if not paths:
            return
        try:
            errors = self.model.import_files(paths)
            self._refresh_all()
            for error in errors:
                QMessageBox.critical(self, "Editor de PDF", error)
        except BaseException as exc:
            report_error(self, "Não foi possível importar o arquivo", exc)

    def run_image_sync(self, token: int, fn, on_done=None) -> None:
        # Renderização deliberadamente serial: PDFium não é chamado em paralelo
        # por preview/miniaturas, evitando acesso nativo concorrente.
        try:
            result = fn()
            if result is None:
                if token == self._preview_token:
                    self.preview.set_image(None, self.model.zoom)
                return
            image = _pil_to_qimage(result)
            if token != self._preview_token:
                return
            if on_done:
                on_done(image)
            else:
                self.preview.set_image(image, self.model.zoom, None)
        except BaseException as exc:
            log.exception("Falha isolada no preview do Editor PDF")
            if token == self._preview_token:
                self.status.setText(f"Falha na visualização: {exc}")

    def refresh_all_sync(self) -> None:
        try:
            selected = self.model.selected_index
            self.thumbs.blockSignals(True)
            self.thumbs.clear()
            for index, page in enumerate(list(self.model.pages)):
                item = QListWidgetItem(str(index + 1))
                item.setData(Qt.ItemDataRole.UserRole, page.uid)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                try:
                    image = _pil_to_qimage(self.model.render_thumbnail(index))
                    item.setIcon(QPixmap.fromImage(image))
                    item.setSizeHint(QSize(80, 108))
                except BaseException:
                    log.exception("Falha isolada ao gerar miniatura PDF %s", index)
                    item.setSizeHint(QSize(80, 46))
                self.thumbs.addItem(item)
            self.thumbs.setVisible(bool(self.model.pages))
            count = len(self.model.pages)
            self.page_count.setText(f"{count} {'página' if count == 1 else 'páginas'}")
            if 0 <= selected < self.thumbs.count():
                self.thumbs.setCurrentRow(selected)
            self.thumbs.blockSignals(False)
            self.zoom_label.setText(f"{round(self.model.zoom * 100)}%")
            self._refresh_cover()
            self._request_preview()
        except BaseException as exc:
            try:
                self.thumbs.blockSignals(False)
            except Exception:
                pass
            report_error(self, "Falha ao atualizar o Editor PDF", exc)

    def export_sync(self) -> None:
        try:
            if not self.model.pages and not self.include_cover.isChecked():
                QMessageBox.critical(
                    self,
                    "Editor de PDF",
                    "Adicione ao menos uma página ou mantenha a capa ativada.",
                )
                return
            default_name = (
                "RADAR DE NOTICIAS - MIDIA IMPRESSA.pdf"
                if self.include_cover.isChecked()
                else "documento.pdf"
            )
            name, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", default_name, "PDF (*.pdf)")
            if not name:
                return
            self.export_button.setEnabled(False)
            self.status.setText("Gerando PDF...")
            path = self.model.export_pdf(
                Path(name),
                include_cover=self.include_cover.isChecked(),
                quality=PdfExportQuality.HIGH,
            )
            self.status.setText(f"PDF gerado com sucesso: {path}")
            box = QMessageBox(self)
            box.setWindowTitle("Exportação concluída")
            box.setText(f"PDF gerado com sucesso!\n{path}")
            box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            folder = box.addButton("Abrir pasta", QMessageBox.ButtonRole.ActionRole)
            box.exec()
            if box.clickedButton() is folder:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))
        except BaseException as exc:
            report_error(self, "Erro ao gerar PDF", exc)
        finally:
            try:
                self.export_button.setEnabled(True)
            except Exception:
                pass

    PdfEditorPage._import = safe_import
    PdfEditorPage._run_image_worker = run_image_sync
    PdfEditorPage._refresh_all = refresh_all_sync
    PdfEditorPage._export = export_sync
