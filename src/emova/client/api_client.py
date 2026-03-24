import json
from urllib.parse import urlencode
from PySide6.QtCore import QObject, Signal, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

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
    profile_success = Signal(dict) # Transmits user dict {"email": "..."}
    profile_error = Signal(str)    # Transmits error message
    
    # Password Change Signals
    change_password_success = Signal(dict) # Transmits confirmation
    change_password_error = Signal(str)    # Transmits error message
    
    # Registration Signals
    register_success = Signal(dict) # Transmits user dict {"id": "...", "email": "..."}
    register_error = Signal(str)    # Transmits error message

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ApiClient()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager(self)
        self.base_url = "http://127.0.0.1:8000"
        self.token = None

    def set_token(self, token: str):
        self.token = token
        
    def _create_json_request(self, endpoint: str) -> QNetworkRequest:
        url = QUrl(f"{self.base_url}{endpoint}")
        req = QNetworkRequest(url)
        req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        if self.token:
            req.setRawHeader(b"Authorization", f"Bearer {self.token}".encode('utf-8'))
        return req

    def _parse_error(self, body: dict) -> str:
        """Extracts readable error text from FastAPI dictionaries or PyDantic Validation 422 Arrays."""
        detail = body.get("detail", "Error desconocido.")
        if isinstance(detail, list) and len(detail) > 0:
            msg = detail[0].get("msg", "Error de validación.")
            return msg.replace("Value error, ", "") # Clean up pydantic prefix
        return str(detail)

    def login(self, email: str, password: str):
        """Dispatches an asynchronous login POST to the OAuth2 form endpoint."""
        url = QUrl(f"{self.base_url}/auth/login")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/x-www-form-urlencoded")
        
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
                    self.token = body.get("access_token")
                    self.login_success.emit(self.token)
                    # Automatically fetch profile to hydrate the UI
                    self.fetch_profile()
                except Exception as e:
                    self.login_error.emit("Failed to parse token from server.")
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.login_error.emit(self._parse_error(body))
                except Exception:
                    self.login_error.emit("No se pudo conectar al servidor backend.")
                    
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
                    self.register_error.emit("Error de parseo del servidor.")
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.register_error.emit(self._parse_error(body))
                except Exception:
                    self.register_error.emit("No se pudo conectar al servidor backend.")
                    
        reply.finished.connect(handle_reply)

    def fetch_profile(self):
        """Asynchronously triggers a GET request to /users/me using the accumulated local token."""
        if not self.token:
            self.profile_error.emit("No token available.")
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
                    self.profile_error.emit("Failed to parse profile response from server.")
            else:
                self.profile_error.emit("Fallo al obtener información de sesión.")
                
        reply.finished.connect(handle_reply)

    def change_password(self, old_password: str, new_password: str):
        """Asynchronously triggers a PUT request to /users/me/password to update credentials."""
        if not self.token:
            self.change_password_error.emit("Sesión no iniciada. No se pudo hacer el cambio.")
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
                    self.change_password_success.emit({"message": "Contraseña actualizada."})
            else:
                try:
                    res_text = reply.readAll().data().decode('utf-8')
                    body = json.loads(res_text)
                    self.change_password_error.emit(self._parse_error(body))
                except Exception:
                    self.change_password_error.emit("Error de red al intentar actualizar la contraseña.")
                    
        reply.finished.connect(handle_reply)
