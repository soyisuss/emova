from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QHBoxLayout, QWidget,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from emova.client.api_client import ApiClient


class HistoryDialog(QDialog):
    def __init__(self, reports, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Reportes Sincronizados")
        self.resize(700, 400)
        self.reports = reports

        self.api_client = ApiClient.get_instance()
        self.api_client.download_report_success.connect(
            self.on_download_success)
        self.api_client.download_report_error.connect(self.on_download_error)

        layout = QVBoxLayout(self)

        title = QLabel("Tus Reportes de EMOVA")
        title.setProperty("class", "HeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        if not self.reports:
            empty_lbl = QLabel(
                "Aún no tienes ningún reporte sincronizado en tu cuenta.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_lbl)

            btn_close = QPushButton("Aceptar")
            btn_close.clicked.connect(self.accept)
            layout.addWidget(btn_close)
            return

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(
            ["Fecha de Creación", "Acción"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 130)

        self.table.setRowCount(len(self.reports))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)

        for row, r in enumerate(self.reports):
            # Parse Date
            created_at = r.get("createdAt", "Fecha desconocida")
            # Limit length formatting if its an ISO string
            if "T" in created_at:
                created_at = created_at.replace("T", " ")[:19]

            report_id = r.get("_id", "N/A")
            # url = r.get("reportUrl", "")

            self.table.setItem(row, 0, QTableWidgetItem(created_at))

            btn_open = QPushButton("Descargar PDF")
            btn_open.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_open.clicked.connect(
                lambda checked=False, rid=report_id: self.trigger_download(rid))

            # Using widget container exactly inside Table element to center it
            widget_container = QWidget()
            btn_layout = QHBoxLayout(widget_container)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(btn_open)

            self.table.setCellWidget(row, 1, widget_container)

        layout.addWidget(self.table)

        btn_close = QPushButton("Cerrar")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def trigger_download(self, report_id: str):
        default_filename = f"Reporte_EMOVA_{report_id}.pdf"
        out_file, _ = QFileDialog.getSaveFileName(
            self,
            "Descargar copia a la computadora...",
            default_filename,
            "Documentos PDF (*.pdf)"
        )
        if out_file:
            QMessageBox.information(
                self, "Obteniendo...", "El archivo se está descargando en segundo plano, por favor espera un momento.")
            self.api_client.download_report(report_id, out_file)

    def on_download_success(self, filepath):
        QMessageBox.information(
            self, "Descarga Exitosa", f"El archivo fue descargado intacto desde Google Cloud hacia su disco duro:\n{filepath}")

    def on_download_error(self, message):
        QMessageBox.critical(self, "Error Técnico", message)

    def closeEvent(self, event):
        try:
            self.api_client.download_report_success.disconnect(
                self.on_download_success)
            self.api_client.download_report_error.disconnect(
                self.on_download_error)
        except Exception:
            pass
        super().closeEvent(event)
