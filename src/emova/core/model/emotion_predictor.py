import os
import numpy as np
import onnxruntime as ort

# Resolvemos la ruta a la raíz del proyecto para evitar errores si el cwd cambia
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "resnet50_emotion.onnx")

class EmotionPredictor:
    """Clase administradora de la sesión de ONNX para no recargarla en cada frame."""
    def __init__(self, model_path=MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"¡Modelo no encontrado en {model_path}! Asegúrate de que resnet50.onnx esté allí.")
        
        # Recomendación técnica: Tratar de usar GPU (CUDA), sino hace fallback automático a CPU.
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        
        # Mapeo oficial del modelo según su entrenamiento
        self.emotions = ["Contento", "Neutral", "Descontento"]

    def predict(self, face_tensor: np.ndarray):
        """
        Ejecuta la inferencia sobre el tensor procesado.
        Puede recibir una sola imagen (3, 224, 224) o un Batch entero (N, 3, 224, 224) para mayor estabilidad.
        :return: (emocion_str, confianza_float) que representa a la mayoría/promedio del Tensor.
        """
        # 1. Adaptar el shape a formato Batch: (B, C, H, W)
        if len(face_tensor.shape) == 3 and face_tensor.shape == (3, 224, 224):
            tensor_input = np.expand_dims(face_tensor, axis=0) # (1, 3, 224, 224)
        elif len(face_tensor.shape) == 4 and face_tensor.shape[1:] == (3, 224, 224):
            tensor_input = face_tensor # Ya es un Batch (N, 3, 224, 224)
        else:
            raise ValueError(f"Shape inválido para ResNet-50. Calculado: {face_tensor.shape}")

        # 2. Asegurarse que el tipo de dato es float32 (Requerimiento de ONNX)
        tensor_input = tensor_input.astype(np.float32)

        # 3. Consumir el modelo (procesa internamente MÚLTIPLES imágenes en milisegundos a la vez)
        raw_output = self.session.run(None, {self.input_name: tensor_input})
        
        # 4. Procesar Logits utilizando Softmax para todas las imágenes del batch
        # raw_output[0] tiene forma (B, número_de_clases_emocionales)
        logits = raw_output[0]
        # Truco matemático para evitar explosión (por filas/batch)
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True)) 
        probabilities = exp_logits / exp_logits.sum(axis=1, keepdims=True)

        # 5. Averiguar la dominancia global (Sacamos el promedio de todas las probabilidades conjuntas del Lote)
        mean_probs = probabilities.mean(axis=0)
        
        # Extraer el ganador estadístico
        max_idx = np.argmax(mean_probs)
        predicted_emotion = self.emotions[max_idx]
        confidence = float(mean_probs[max_idx])

        return predicted_emotion, round(confidence, 2)


# Singleton para exportar la misma función que usabas en `camera_thread.py`
# pero inyectando el tensor real ahora mediante ONNX.
_predictor_instance = None

def predict_emotion(face_tensor: np.ndarray):
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = EmotionPredictor()
        
    return _predictor_instance.predict(face_tensor)