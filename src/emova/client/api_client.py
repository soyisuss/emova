import os
import json
from urllib.parse import urlencode
from PySide6.QtCore import QObject, Signal, QUrl, QByteArray, QFile, QSettings
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QHttpMultiPart, QHttpPart


class ApiClient(QObject):
    """
    Cliente API tipo Singleton para manejar peticiones HTTP asíncronas con el backend FastAPI de Emova.
    """
    _instance = None

    # Señales para autenticación
    login_success = Signal(str)    # Transmite el token JWT al iniciar sesión correctamente
    login_error = Signal(str)      # Transmite el mensaje de error de inicio de sesión

    # Señales para el perfil de usuario
    profile_success = Signal(dict)  # Transmite el diccionario del usuario {"email": "..."}
    profile_error = Signal(str)    # Transmite el mensaje de error al consultar el perfil

    # Señales para cambio de contraseña
    change_password_success = Signal(dict)  # Transmite la confirmación del cambio
    change_password_error = Signal(str)    # Transmite el mensaje de error del cambio

    # Señales para registro de usuario
    # Transmite el diccionario del usuario registrado {"id": "...", "email": "..."}
    register_success = Signal(dict)
    register_error = Signal(str)    # Transmite el mensaje de error al registrar

    # Señales para recuperación de contraseña
    forgot_password_success = Signal(dict)
    forgot_password_error = Signal(str)
    reset_password_success = Signal(dict)
    reset_password_error = Signal(str)

    # Señales para envío de reportes
    upload_report_success = Signal(dict)
    upload_report_error = Signal(str)

    # Señales para visualización del historial
    history_success = Signal(list)
    history_error = Signal(str)

    # Señales para descarga de reportes
    download_report_success = Signal(str)
    download_report_error = Signal(str)

    # Señales para eliminación de reportes
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
        # Configuración de la URL base para el entorno de producción (Google Cloud Run)
        self.base_url = "https://emova-api-490638015196.us-central1.run.app"

        # Configuración para la persistencia local del token de sesión
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
        """
        Extrae un mensaje de error legible a partir de diccionarios de FastAPI o arreglos de PyDantic.
        """
        detail = body.get("detail", "Error desconocido.")
        if isinstance(detail, list) and len(detail) > 0:
            msg = detail[0].get("msg", "Error de validación.")
            return f"[{error_code}] {msg.replace('Value error, ', '')}"  # Elimina el prefijo pydantic
        return f"[{error_code}] {str(detail)}"

    def login(self, email: str, password: str):
        """
        Realiza una petición POST asíncrona para iniciar sesión.
        """
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
                    # Consulta el perfil automáticamente para actualizar la interfaz
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
        """
        Registra un nuevo usuario enviando una petición POST asíncrona al backend.
        """
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
        """
        Obtiene la información del perfil del usuario actual mediante una petición GET asíncrona.
        """
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
        """
        Modifica la contraseña del usuario actual mediante una petición PUT asíncrona.
        """
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

        # Utiliza el método PUT definido en el controlador del backend
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
        """
        Solicita un código de recuperación de contraseña mediante una petición POST asíncrona.
        """
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
        """
        Restablece la contraseña utilizando el código de verificación recibido.
        """
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
        """
        Sube el reporte en formato PDF al servidor mediante una petición POST multipart asíncrona.
        """
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
        """
        Descarga el historial de reportes asociados al usuario mediante una petición GET asíncrona.
        """
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
        """
        Descarga los bytes crudos del reporte PDF a través de la API para omitir la seguridad del bucket.
        """
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
        """
        Elimina el registro de un reporte a través de una petición DELETE asíncrona al backend.
        """
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
