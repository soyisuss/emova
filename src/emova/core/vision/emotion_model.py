import numpy as np
import onnxruntime as ort

class EmotionRecognizer:
    def __init__(self, model_path: str, labels=None):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        # El modelo tiene 3 salidas. Asumimos este orden, pero se puede sobrescribir.
        if labels is None:
            self.labels = ["Negativo", "Neutral", "Positivo"]
        else:
            self.labels = labels

    def predict(self, face_tensor: np.ndarray) -> tuple[str, float, dict]:
        """
        Recibe un tensor preprocesado de dimensiones (3, 224, 224) 
        Devuelve (etiqueta_ganadora, confidencia, probabilidades_completas)
        """
        # Añadir la dimensión de batch, PyTorch/ONNX espera: (1, 3, 224, 224)
        input_tensor = np.expand_dims(face_tensor, axis=0)
        
        # Inferir a través del modelo ONNX
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})[0]
        
        # El modelo devuelve logits. Aplicamos una función Softmax para transformarlo en probabilidades (0-1).
        logits = outputs[0]
        exp_vals = np.exp(logits - np.max(logits)) # Restamos el max para estabilidad numérica
        probs = exp_vals / np.sum(exp_vals)
        
        # Determinar la emoción dominante
        max_idx = np.argmax(probs)
        ganadora = self.labels[max_idx]
        confidencia = float(probs[max_idx])
        
        # Diccionario con el porcentaje de cada emoción
        todas = {self.labels[i]: float(probs[i]) for i in range(min(len(self.labels), len(probs)))}
        
        return ganadora, confidencia, todas
