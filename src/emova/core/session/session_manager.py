import httpx

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
            resp = httpx.get("http://127.0.0.1:8000/tests/templates/", timeout=2.0)
            if resp.status_code == 200:
                count = len(resp.json())
                self.test_id = f"PU-{count + 1:02d}"
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
