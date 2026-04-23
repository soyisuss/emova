from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import os

from emova.core.session.session_manager import session_manager
from emova.core.reporting.report_generator import generate_pdf_report
from emova.client.gui.components.custom_dialog import CustomDialog
from emova.client.gui.components.history_dialog import HistoryDialog
from emova.client.api_client import ApiClient


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)

        layout.addStretch()  # Empuja hacia abajo para centrar

        # Absolute path to assets/images
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.abspath(os.path.join(
            current_dir, "..", "assets", "images"))

        # Generar reporte
        lbl_generate = QLabel("Generar reporte")
        lbl_generate.setProperty("class", "SidebarLabel")
        lbl_generate.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_generate = QPushButton()
        icon_generate = QIcon(os.path.join(icons_dir, "archivo.png"))
        btn_generate.setIcon(icon_generate)
        btn_generate.setIconSize(QSize(55, 55))
        btn_generate.setProperty("class", "SidebarButton")
        btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_generate.clicked.connect(self.trigger_pdf_generation)

        layout.addWidget(lbl_generate)
        layout.addWidget(btn_generate)

        # El botón de descargar fue eliminado por redundancia dado que Generar Reporte ya salva el archivo.

        # Historial de reportes
        lbl_history = QLabel("Historial de reportes")
        lbl_history.setProperty("class", "SidebarLabel")
        lbl_history.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_history = QPushButton()
        icon_history = QIcon(os.path.join(icons_dir, "historial.png"))
        btn_history.setIcon(icon_history)
        btn_history.setIconSize(QSize(55, 55))
        btn_history.setProperty("class", "SidebarButton")
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_history.clicked.connect(self.trigger_history_fetch)

        layout.addWidget(lbl_history)
        layout.addWidget(btn_history)

        layout.addStretch()  # Empuja hacia arriba para centrar balanceadamente

        self.api_client = ApiClient.get_instance()
        self.api_client.upload_report_success.connect(
            self.on_upload_report_success)
        self.api_client.upload_report_error.connect(
            self.on_upload_report_error)
        self.api_client.history_success.connect(self.on_history_success)
        self.api_client.history_error.connect(self.on_history_error)

    def trigger_history_fetch(self):
        """Dispara la petición para traer los reportes históricos y mostrarlos."""
        self.api_client.fetch_history()

    def trigger_pdf_generation(self):
        data = session_manager.get_report_data()

        # Native OS Save Dialog
        test_id = session_manager.test_id if hasattr(
            session_manager, 'test_id') else "Desconocido"
        default_filename = f"Reporte_EMOVA_{test_id}.pdf"
        file_filter = "Documentos PDF (*.pdf)"

        out_file, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte EMOVA como...",
            default_filename,
            file_filter
        )

        # If user cancelled the dialog, out_file will be empty string
        if not out_file:
            return

        try:
            generate_pdf_report(data, out_file)

            # Subir asincrónicamente a Google Cloud Storage mediante FastAPI
            self.api_client.upload_report(out_file, test_name=f"Prueba de Usabilidad {test_id}")

            # Reiniciar la sesión de prueba automáticamente tras generar reporte
            session_manager.reset_session()

            # Actualizar el Header visial en MainWindow para mostrar el nuevo ID de prueba
            main_win = self.window()
            if hasattr(main_win, 'header') and hasattr(main_win.header, 'project_label'):
                main_win.header.project_label.setText(session_manager.test_id)

            # Show the centered Modal explicitly requiring user to press "Aceptar"
            dialog = CustomDialog(
                parent=self.window(),
                title="Sincronizando...",
                message=f"PDF generado localmente en:\n{os.path.basename(out_file)}\n\nSubiendo una copia segura a Google Cloud Storage en segundo plano..."
            )
            dialog.exec()

        except Exception as e:
            dialog = CustomDialog(
                parent=self.window(),
                title="Error al Generar",
                message=f"Sucedió un error creando el reporte PDF:\n{str(e)}"
            )
            dialog.exec()

    def on_upload_report_success(self, response_data):
        dialog = CustomDialog(
            parent=self.window(),
            title="Sincronización Exitosa",
            message="El último reporte se subió correctamente a Google Cloud y ahora forma parte de tu historial."
        )
        dialog.exec()

    def on_upload_report_error(self, message):
        dialog = CustomDialog(
            parent=self.window(),
            title="Error de Sincronización",
            message=f"Se generó el archivo local pero falló su subida a la Nube:\n{message}"
        )
        dialog.exec()

    def on_history_success(self, reports_list):
        dialog = HistoryDialog(reports=reports_list, parent=self.window())
        dialog.exec()

    def on_history_error(self, message):
        dialog = CustomDialog(
            parent=self.window(),
            title="Aviso",
            message=message
        )
        dialog.exec()
