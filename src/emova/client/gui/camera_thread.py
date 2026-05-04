import os
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from emova.core.capture.camera import open_source, read_frame
from emova.core.capture.fps_sampler import FPSSampler
from emova.core.model.emotion_predictor import predict_emotion
from emova.core.vision.face_detector import FaceDetector
from emova.core.vision.pipeline import VideoPreprocessingPipeline


class CameraThread(QThread):
    # Signals to emit frames and prediction data back to the main UI thread
    frame_ready = Signal(np.ndarray)
    emotion_ready = Signal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self.camera_index = 0
        self.cap = None
        self.is_detecting = False
        self.sampler = FPSSampler(3)  # Process every 3rd frame
        self._tensor_batch_buffer = []  # Buffer limitador para el modelo de IA
        # Por ej. a 3 FPS de extracción, juntará imágenes durante 1 segundo entero.
        self.batch_size = 3

        # Inicializar pipeline de preprocesamiento usando rutas absolutas
        project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", ".."))
        proto = os.path.join(project_root, "models", "deploy.prototxt")
        model = os.path.join(project_root, "models",
                             "res10_300x300_ssd_iter_140000_fp16.caffemodel")

        try:
            self.detector = FaceDetector(proto, model)
            self.pipeline = VideoPreprocessingPipeline(self.detector)
        except Exception as e:
            print(
                f"Error inicializando pipeline (modelos posiblemente faltantes): {e}")
            self.pipeline = None

    def run(self):
        self._is_running = True
        self.cap = open_source(self.camera_index)

        while self._is_running:
            frame = read_frame(self.cap)

            if frame is None:
                continue

            display_frame = frame.copy()

            if self.pipeline:
                results = self.pipeline.process_frame(frame)

                # Dibujar recuadros en los rostros detectados
                for res in results:
                    x1, y1, x2, y2 = res["box"]
                    cv2.rectangle(display_frame, (x1, y1),
                                  (x2, y2), (0, 255, 0), 2)

                # Extraer preprocesamiento sólo si es momento en base al sampleo, si hay caras, y si se está detectando activamente
                if len(results) > 0 and self.sampler.should_process() and self.is_detecting:
                    # Acumulamos el primer rostro detectado (si hubiera varios, tomamos el principal)
                    tensor = results[0]["face_tensor"]
                    self._tensor_batch_buffer.append(tensor)

                    # Disparamos la red neuronal ONNX sólo cuando la caja se llena
                    if len(self._tensor_batch_buffer) >= self.batch_size:
                        # Combinamos todas las imágenes recolectadas en una sola matriz maestra: (N, 3, 224, 224)
                        batch_tensor = np.stack(
                            self._tensor_batch_buffer, axis=0)

                        # Predecimos una vez (el resultado ahora será la dominancia estadística de todos esos cuadros)
                        emotion, conf = predict_emotion(batch_tensor)

                        # Imprimir en la terminal para dar visibilidad técnica durante el Testing
                        print(
                            f"\n[IA-CORE] Lote de {self.batch_size} tensores procesado -> Emoción dominante: {emotion} | Confianza media: {conf * 100:.1f}%",
                            flush=True,
                        )

                        self.emotion_ready.emit(emotion, conf)

                        # Vaciamos la caja para esperar las siguientes capturas
                        self._tensor_batch_buffer.clear()

            # Emitir para la vista en el VideoPlayer
            self.frame_ready.emit(display_frame)

            # Sleep slightly to allow thread switching (~33fps)
            self.msleep(30)

        if self.cap is not None:
            self.cap.release()

    def stop(self):
        self._is_running = False
        self.wait()  # Block until thread finishes
