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
        self.calibration_data = {} # Baseline calibration data
        
    def set_calibration(self, phase: str, emotion: str, confidence: float):
        """Stored the baseline calibration emotion for positive or negative stimuli."""
        self.calibration_data[phase] = {
            "emotion": emotion,
            "confidence": confidence
        }
        
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
            "survey": self.survey,
            "calibration_data": self.calibration_data
        }

# Global singleton instance to be imported across the application
session_manager = SessionManager()
