"""
Módulo para la gestión de la tarea de usabilidad activa actualmente en el cliente.
"""

class TaskManager:
    """
    Administra el estado de la tarea de usabilidad que se está ejecutando.
    """

    def __init__(self):
        self.current_task = None


    def start_task(self, name):
        """
        Establece la tarea activa por su nombre.
        """
        self.current_task = name


    def stop_task(self):
        """
        Finaliza la tarea activa, limpiando el estado.
        """
        self.current_task = None