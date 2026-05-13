import httpx
from emova.client.api_client import ApiClient

class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.reset_session()
        return cls._instance
        
    def reset_session(self):
        """Clear all active session data starting fresh."""
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
                    # Encontrar un límite seguro superior
                    next_id = max(max_num + 1, len(templates) + 1)
                    self.test_id = f"PU-{next_id:02d}"
        except Exception:
            pass
            
        self.participant = {}
        self.tasks = []
        self.emotions = []  # Placeholder for future emotion data per task
        self.survey = {}    # Placeholder for future survey results
        
    def set_participant(self, participant_data):
        self.participant = participant_data
        
    def add_task(self, title, description):
        self.tasks.append({
            "title": title,
            "description": description
        })
        
    def clear_tasks(self):
        """Removes all currently recorded tasks (used when re-saving from Task registration)."""
        self.tasks = []
        
    def get_report_data(self):
        """Returns the centralized snapshot of all testing data."""
        return {
            "test_id": self.test_id,
            "participant": self.participant,
            "tasks": self.tasks,
            "emotions": self.emotions,
            "survey": self.survey
        }

# Global singleton instance to be imported across the application
session_manager = SessionManager()
