"""
Módulo para controlar la tasa de procesamiento por segundo (FPS) de los fotogramas de la cámara.
"""
import time

class FPSSampler:
    """
    Controla el muestreo de fotogramas por segundo para evitar sobrecargar el modelo de IA.
    """

    def __init__(self, fps=3):
        """
        Inicializa el muestreador con los FPS objetivo (por defecto, 3 FPS).
        """
        self.interval = 1.0 / fps
        self.last_time = 0


    def should_process(self):
        """
        Determina si ha transcurrido suficiente tiempo para procesar el siguiente fotograma.
        """
        now = time.time()

        if now - self.last_time >= self.interval:
            self.last_time = now
            return True

        return False