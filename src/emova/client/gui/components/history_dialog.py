from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QHBoxLayout, QWidget,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from emova.client.api_client import ApiClient


class HistoryDialog(QDialog):
    def __init__(self, reports, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Reportes Sincronizados")
        self.resize(700, 400)
        self.reports = reports
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9fc;
            }
            QLabel {
                color: #333333;
            }
            QLabel[class="HeaderLabel"] {
                font-size: 22px;
                font-weight: bold;
                color: #7E38B7;
                margin-bottom: 10px;
            }
            QTableWidget {
                background-color: white;
                color: #333333;
                border: 2px solid #7E38B7;
                border-radius: 8px;
                gridline-color: #e0e0e0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #7E38B7;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 6px;
                border: 1px solid #7E38B7;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QPushButton[class="TableButton"] {
                background-color: #7E38B7;
                color: white;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton[class="TableButton"]:hover {
                background-color: #5e288e;
            }
        """)

        self.api_client = ApiClient.get_instance()
        self.api_client.download_report_success.connect(self.on_download_success)
        self.api_client.download_report_error.connect(self.on_download_error)
        self.api_client.delete_report_success.connect(self.on_delete_success)
        self.api_client.delete_report_error.connect(self.on_delete_error)

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
            btn_close.setProperty("class", "DialogButton")
            btn_close.clicked.connect(self.accept)
            layout.addWidget(btn_close)
            return

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Identificador", "Fecha de Creación", "Acciones"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 220)
        self.table.verticalHeader().setDefaultSectionSize(45)

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

            test_name = r.get("testName", "Prueba General")
            report_id = r.get("_id", "N/A")

            self.table.setItem(row, 0, QTableWidgetItem(test_name))
            self.table.setItem(row, 1, QTableWidgetItem(created_at))

            btn_open = QPushButton(" Descargar")
            btn_open.setProperty("class", "TableButton")
            btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn_del = QPushButton(" Eliminar")
            btn_del.setStyleSheet("background-color: #d9534f; color: white; border-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 12px;")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)

            current_dir = os.path.dirname(os.path.abspath(__file__))
            icons_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "images"))
            btn_open.setIcon(QIcon(os.path.join(icons_dir, "download.svg")))

            btn_open.clicked.connect(lambda checked=False, rid=report_id: self.trigger_download(rid))
            btn_del.clicked.connect(lambda checked=False, rid=report_id: self.trigger_delete(rid))

            widget_container = QWidget()
            btn_layout = QHBoxLayout(widget_container)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(btn_open)
            btn_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 2, widget_container)

        layout.addWidget(self.table)

        btn_close = QPushButton("Cerrar")
        btn_close.setProperty("class", "DialogButton")
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

    def trigger_delete(self, report_id: str):
        res = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro que deseas eliminar este reporte permanentemente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            self.api_client.delete_report(report_id)

    def on_delete_success(self, data):
        QMessageBox.information(self, "Eliminado", "El reporte se eliminó correctamente de la nube.")
        self.accept() # Cerrar para que recarguen
        self.api_client.fetch_history() # Disparar recarga en cadena si el componente padre lo observa

    def on_delete_error(self, message):
        QMessageBox.warning(self, "Error al eliminar", message)

    def closeEvent(self, event):
        try:
            self.api_client.download_report_success.disconnect(self.on_download_success)
            self.api_client.download_report_error.disconnect(self.on_download_error)
            self.api_client.delete_report_success.disconnect(self.on_delete_success)
            self.api_client.delete_report_error.disconnect(self.on_delete_error)
        except Exception:
            pass
        super().closeEvent(event)
