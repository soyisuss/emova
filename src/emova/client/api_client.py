import os
import json
from urllib.parse import urlencode
from PySide6.QtCore import QObject, Signal, QUrl, QByteArray, QFile, QSettings
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QHttpMultiPart, QHttpPart


class ApiClient(QObject):
    """
    Singleton API Client to handle asynchronous HTTP requests interacting
    with the Emova FastAPI Backend.
    """
    _instance = None

    # Auth Signals
    login_success = Signal(str)    # Transmits token
    login_error = Signal(str)      # Transmits error message

    # Profile Signals
    profile_success = Signal(dict)  # Transmits user dict {"email": "..."}
    profile_error = Signal(str)    # Transmits error message

    # Password Change Signals
    change_password_success = Signal(dict)  # Transmits confirmation
    change_password_error = Signal(str)    # Transmits error message

    # Registration Signals
    # Transmits user dict {"id": "...", "email": "..."}
    register_success = Signal(dict)
    register_error = Signal(str)    # Transmits error message

    # Recovery Signals
    forgot_password_success = Signal(dict)
    forgot_password_error = Signal(str)
    reset_password_success = Signal(dict)
    reset_password_error = Signal(str)

    # Report Submitting Signals
    upload_report_success = Signal(dict)
    upload_report_error = Signal(str)

    # History viewing signals
    history_success = Signal(list)
    history_error = Signal(str)

    # Download signals
    download_report_success = Signal(str)
    download_report_error = Signal(str)

    # Delete signals
    delete_report_success = Signal(dict)
    delete_report_error = Signal(str)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ApiClient()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager(self)
        # Apuntando a tu nueva API en Producción (Google Cloud Run)
        self.base_url = "https://emova-api-490638015196.us-central1.run.app"

        # Persistencia en Disco / Registro nativo
        self.settings = QSettings("EMOVA", "EmovaClient")
        self.token = self.settings.value("auth_token", None)

    def set_token(self, token: str):
        self.token = token
        if token:
            self.settings.setValue("auth_token", token)
        else:
            self.settings.remove("auth_token")

    def _create_json_request(self, endpoint: str) -> QNetworkRequest:
        url = QUrl(f"{self.base_url}{endpoint}")
        req = QNetworkRequest(url)
        req.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        if self.token:
            req.setRawHeader(b"Authorization",
                             f"Bearer {self.token}".encode('utf-8'))
        return req

    def _parse_error(self, body: dict, error_code: str = "ERR_API_00") -> str:
        """Extracts readable error text from FastAPI dictionaries or PyDantic Validation 422 Arrays."""
        detail = body.get("detail", "Error desconocido.")
        if isinstance(detail, list) and len(detail) > 0:
            msg = detail[0].get("msg", "Error de validación.")
            return f"[{error_code}] {msg.replace('Value error, ', '')}"  # Clean up pydantic prefix
        return f"[{error_code}] {str(detail)}"

    def login(self, email: str, password: str):
        """Dispatches an asynchronous login POST to the OAuth2 form endpoint."""
        url = QUrl(f"{self.base_url}/auth/login")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader,
                          "application/x-www-form-urlencoded")

        payload = {"username": email, "password": password}
        query_string = urlencode(payload)
        data = QByteArray(query_string.encode('utf-8'))

        reply = self.manager.post(request, data)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.set_token(body.get("access_token"))
                    self.login_success.emit(self.token)
                    # Automatically fetch profile to hydrate the UI
                    self.fetch_profile()
                except Exception as e:
                    self.login_error.emit(
                        f"[ERR_AUTH_01] Error al parsear el token: {e}")
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.login_error.emit(self._parse_error(body, "ERR_AUTH_02"))
                except Exception:
                    self.login_error.emit(
                        "[ERR_NET_01] No se pudo conectar al servidor backend.")

        reply.finished.connect(handle_reply)

    def register(self, email: str, password: str):
        """Dispatches an asynchronous signup POST to the users JSON endpoint."""
        request = self._create_json_request("/users/")

        payload = {
            "email": email,
            "password": password
        }
        data = QByteArray(json.dumps(payload).encode('utf-8'))

        reply = self.manager.post(request, data)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.register_success.emit(body)
                except Exception:
                    self.register_error.emit("[ERR_SRV_01] Error de parseo del servidor.")
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.register_error.emit(self._parse_error(body, "ERR_API_01"))
                except Exception:
                    self.register_error.emit(
                        "[ERR_NET_01] No se pudo conectar al servidor backend.")

        reply.finished.connect(handle_reply)

    def fetch_profile(self):
        """Asynchronously triggers a GET request to /users/me using the accumulated local token."""
        if not self.token:
            self.profile_error.emit("[ERR_AUTH_03] Sesión no iniciada.")
            return

        request = self._create_json_request("/users/me")
        reply = self.manager.get(request)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.profile_success.emit(body)
                except Exception:
                    self.profile_error.emit(
                        "[ERR_SRV_02] Error al parsear información del perfil.")
            else:
                self.profile_error.emit(
                    "[ERR_NET_02] Fallo al obtener información de sesión.")

        reply.finished.connect(handle_reply)

    def change_password(self, old_password: str, new_password: str):
        """Asynchronously triggers a PUT request to /users/me/password to update credentials."""
        if not self.token:
            self.change_password_error.emit(
                "[ERR_AUTH_03] Sesión no iniciada. No se pudo hacer el cambio.")
            return

        request = self._create_json_request("/users/me/password")

        payload = {
            "old_password": old_password,
            "new_password": new_password
        }
        data = QByteArray(json.dumps(payload).encode('utf-8'))

        # Use PUT as specified in users.py
        reply = self.manager.put(request, data)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.change_password_success.emit(body)
                except Exception:
                    self.change_password_success.emit(
                        {"message": "Contraseña actualizada."})
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.change_password_error.emit(self._parse_error(body, "ERR_API_02"))
                except Exception:
                    self.change_password_error.emit(
                        "[ERR_NET_03] Error de red al intentar actualizar la contraseña.")

        reply.finished.connect(handle_reply)

    def forgot_password(self, email: str):
        """Asynchronously triggers a POST request to /auth/forgot-password to request a recovery code."""
        request = self._create_json_request("/auth/forgot-password")

        payload = {"email": email}
        data = QByteArray(json.dumps(payload).encode('utf-8'))

        reply = self.manager.post(request, data)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.forgot_password_success.emit(body)
                except Exception:
                    self.forgot_password_success.emit(
                        {"message": "Código enviado si el correo existe."})
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.forgot_password_error.emit(self._parse_error(body, "ERR_API_03"))
                except Exception:
                    self.forgot_password_error.emit(
                        "[ERR_NET_04] Error de red al intentar recuperar contraseña.")

        reply.finished.connect(handle_reply)

    def reset_password(self, email: str, code: str, new_password: str):
        """Asynchronously triggers a POST request to /auth/reset-password to set a new password."""
        request = self._create_json_request("/auth/reset-password")

        payload = {
            "email": email,
            "code": code,
            "new_password": new_password
        }
        data = QByteArray(json.dumps(payload).encode('utf-8'))

        reply = self.manager.post(request, data)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.reset_password_success.emit(body)
                except Exception:
                    self.reset_password_success.emit(
                        {"message": "Contraseña actualizada."})
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.reset_password_error.emit(self._parse_error(body, "ERR_API_04"))
                except Exception:
                    self.reset_password_error.emit(
                        "[ERR_NET_05] Error de red al intentar restablecer contraseña.")

        reply.finished.connect(handle_reply)

    def upload_report(self, filepath: str, test_name: str = "Prueba General"):
        """Asynchronously triggers a POST request to /reports/upload with a Multipart PDF file."""
        if not self.token:
            self.upload_report_error.emit(
                "[ERR_AUTH_03] Sesión no iniciada. No se puede subir el archivo.")
            return

        url = QUrl(f"{self.base_url}/reports/upload")
        request = QNetworkRequest(url)
        if self.token:
            request.setRawHeader(
                b"Authorization", f"Bearer {self.token}".encode('utf-8'))

        multi_part = QHttpMultiPart(QHttpMultiPart.ContentType.FormDataType)

        file = QFile(filepath)
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            self.upload_report_error.emit(
                "[ERR_IO_01] No se pudo abrir el reporte localmente para subida.")
            return

        file_part = QHttpPart()
        filename = os.path.basename(filepath)
        file_part.setHeader(QNetworkRequest.KnownHeaders.ContentDispositionHeader,
                            f'form-data; name="file"; filename="{filename}"')
        file_part.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/pdf")
        file_part.setBodyDevice(file)

        file.setParent(multi_part)
        multi_part.append(file_part)

        name_part = QHttpPart()
        name_part.setHeader(QNetworkRequest.KnownHeaders.ContentDispositionHeader, 'form-data; name="testName"')
        name_part.setBody(test_name.encode('utf-8'))
        multi_part.append(name_part)

        reply = self.manager.post(request, multi_part)
        multi_part.setParent(reply)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.upload_report_success.emit(body)
                except Exception:
                    self.upload_report_error.emit(
                        "[ERR_SRV_03] Error de parseo en la respuesta del servidor.")
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.upload_report_error.emit(self._parse_error(body, "ERR_API_05"))
                except Exception:
                    self.upload_report_error.emit(
                        "[ERR_NET_06] Error de red al intentar subir archivo.")

        reply.finished.connect(handle_reply)

    def fetch_history(self):
        """Asynchronously triggers a GET request to /reports/."""
        if not self.token:
            self.history_error.emit("[ERR_AUTH_03] Sesión no iniciada.")
            return

        request = self._create_json_request("/reports/")
        reply = self.manager.get(request)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.history_success.emit(body)
                except Exception:
                    self.history_error.emit(
                        "[ERR_SRV_04] Error al parsear el historial desde el servidor.")
            else:
                self.history_error.emit(
                    "[ERR_NET_07] Fallo de red al intentar descargar el historial.")

        reply.finished.connect(handle_reply)

    def download_report(self, report_id: str, out_file: str):
        """Asynchronously pulls raw bytes from API proxy to bypass GCS permissions."""
        if not self.token:
            self.download_report_error.emit("[ERR_AUTH_03] Sesión no iniciada.")
            return

        request = self._create_json_request(f"/reports/{report_id}/download")
        reply = self.manager.get(request)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                try:
                    pdf_bytes = reply.readAll().data()
                    with open(out_file, "wb") as f:
                        f.write(pdf_bytes)
                    self.download_report_success.emit(out_file)
                except Exception:
                    self.download_report_error.emit(
                        "[ERR_IO_02] No se pudo escribir el archivo en tu sistema de archivos.")
            else:
                self.download_report_error.emit(
                    "[ERR_NET_08] Fallo de red al intentar descargar el reporte.")

        reply.finished.connect(handle_reply)

    def delete_report(self, report_id: str):
        """Asynchronously triggers a DELETE request to /reports/{report_id} to remove the report metadata."""
        if not self.token:
            self.delete_report_error.emit("[ERR_AUTH_03] Sesión no iniciada. No se puede eliminar.")
            return

        request = self._create_json_request(f"/reports/{report_id}")
        reply = self.manager.deleteResource(request)

        def handle_reply():
            reply.deleteLater()
            if reply.error() == QNetworkReply.NetworkError.NoError:
                self.delete_report_success.emit({"message": "Reporte borrado exitosamente.", "id": report_id})
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.delete_report_error.emit(self._parse_error(body, "ERR_API_06"))
                except Exception:
                    self.delete_report_error.emit("[ERR_NET_09] Fallo de red al intentar eliminar el reporte.")

        reply.finished.connect(handle_reply)
