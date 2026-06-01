"""
Módulo del administrador de sesión. Centraliza los datos temporales del participante y la prueba.
"""
import httpx
from emova.client.api_client import ApiClient


class SessionManager:
    """
    Administra la sesión de prueba activa, incluyendo datos del participante,
    tareas a realizar, emociones registradas y la encuesta final.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.reset_session()
        return cls._instance
        
    def reset_session(self):
        """
        Limpia los datos de la sesión activa para iniciar una nueva prueba.
        """
        self.test_id = "PU-01"
        try:
            api_client = ApiClient.get_instance()
            token = api_client.token
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            base_url = api_client.base_url
            resp = httpx.get(f"{base_url}/tests/templates/", headers=headers, timeout=2.0)
            if resp.status_code == 200:
                templates = resp.json()
                if templates:
                    max_num = 0
                    for t in templates:
                        tid = t.get("test_id", "")
                        if tid and tid.startswith("PU-"):
                            try:
                                num = int(tid.split("-")[1])
                                if num > max_num:
                                    max_num = num
                            except ValueError:
                                pass
                    # Encontrar un límite seguro superior para el siguiente ID de prueba
                    next_id = max(max_num + 1, len(templates) + 1)
                    self.test_id = f"PU-{next_id:02d}"
        except Exception:
            pass
            
        self.participant = {}
        self.tasks = []
        self.emotions = []  # Datos de emociones detectadas por tarea
        self.survey = {}    # Resultados de la encuesta final de usabilidad
        
    def set_participant(self, participant_data):
        """
        Registra la información demográfica del participante en la sesión.
        """
        self.participant = participant_data
        
    def add_task(self, title, description):
        """
        Agrega una tarea de usabilidad a la sesión activa.
        """
        self.tasks.append({
            "title": title,
            "description": description
        })
        
    def clear_tasks(self):
        """
        Remueve todas las tareas registradas de la sesión activa.
        """
        self.tasks = []
        
    def get_report_data(self):
        """
        Retorna una captura centralizada de todos los datos recopilados durante la prueba.
        """
        return {
            "test_id": self.test_id,
            "participant": self.participant,
            "tasks": self.tasks,
            "emotions": self.emotions,
            "survey": self.survey
        }

# Instancia global (Singleton) para ser importada en toda la aplicación
session_manager = SessionManager()

