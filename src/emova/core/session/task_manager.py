class TaskManager:

    def __init__(self):

        self.current_task = None


    def start_task(self,name):

        self.current_task = name


    def stop_task(self):

        self.current_task = None