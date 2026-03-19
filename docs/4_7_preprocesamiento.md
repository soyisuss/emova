# 4.7 Selección y preprocesamiento de fotogramas (Implementación)

Este documento detalla la implementación técnica y matemática de los requisitos de la sección 4.7 de EMOVA. El flujo completo ha sido centralizado a través de la clase `VideoPreprocessingPipeline` (`src/emova/core/vision/pipeline.py`), la cual orquesta secuencialmente las transformaciones de cada fotograma para alimentar la Red Neuronal de forma óptima.

---

## 4.7.1 Captura de video
**Módulo:** `src/emova/core/capture/camera.py`

Cada video o transmisión en vivo se compone de una secuencia de imágenes (fotogramas). Se utilizó `cv2.VideoCapture` de OpenCV para interactuar directamente con el hardware de video o decodificar el flujo del codec (por ejemplo, MP4/H.264) a matrices de NumPy. 

```python
import cv2

def open_source(source=0):
    """Abre la cámara web o un archivo de video."""
    if isinstance(source, int):
        # Utiliza DirectShow en Windows para un acceso más rápido a la cámara web
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
    else:
        # Lee un flujo de video pregrabado desde un archivo
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise Exception(f"No se pudo abrir la fuente de video: {source}")
    return cap

def read_frame(cap):
    # .read() recupera el siguiente frame en formato BGR [H, W, 3]
    ret, frame = cap.read()
    if not ret:
        return None
    return frame
```

---

## 4.7.2 Detección de rostros
**Módulo:** `src/emova/core/vision/face_detector.py`

Acorde a la arquitectura planeada, se importó un modelo Deep Neural Network (DNN) del tipo **Single Shot Multibox Detector (SSD)** basado en la red **ResNet-10**. Se aprovecha el modelo preentrenado nativo de OpenCV con pesos del dataset de rostros WIDER FACE.

Este modelo es altamente eficiente ya que predice múltiples recuadros faciales (bounding boxes) y su probabilidad en una única pasada (`forward()`).

```python
import cv2
import numpy as np

class FaceDetector:
    def __init__(self, proto, model):
        # Se cargan los pesos estadísticos (caffemodel) y su arquitectura (prototxt)
        self.net = cv2.dnn.readNetFromCaffe(proto, model)

    def detect(self, frame):
        # Se convierte la matriz a un 'blob' de (300x300), el tamaño de entrada requerido por el SSD
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
        self.net.setInput(blob)
        return self.net.forward()

    def get_faces(self, frame, confidence_threshold=0.5):
        h, w = frame.shape[:2]
        detections = self.detect(frame)
        faces = []
        
        # Iterar sobre las detecciones extraídas de la red
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Solo procesar detecciones con alta probabilidad de ser un rostro humano
            if confidence > confidence_threshold:
                # Las coordenadas devueltas están normalizadas (0 a 1), se escalan al tamaño real (w, h)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX, endY))
                
        return faces
```

---

## 4.7.3 Verificación del enfoque
**Módulo:** `src/emova/core/vision/focus_validator.py`

Según el análisis comparativo de la Tabla 43, se eligió la métrica basada en la **Varianza del Laplaciano** por su alto rendimiento en tiempo real y solidez para ignorar fotogramas borrosos (motion blur).

El Operador Laplaciano ($∇^2 f$) detecta bordes acentuando grandes derivadas espaciales de segunda orden. Una imagen nítida posee gran variedad de bordes intensos (alta varianza estadística de las mediciones de los bordes), mientras que una borrosa presentará valores muy planos. 

```python
import cv2

def focus_score(frame):
    # La imagen siempre se evalúa en escala de grises para operaciones de derivadas
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Se aplica una profundidad de píxel flotante de 64 bits (CV_64F) para no perder signos negativos
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def is_blurry(frame, threshold=80):
    # Si la varianza (nitidez) es menor a 80, el frame se descarta
    return focus_score(frame) < threshold
```

---

## 4.7.4 Recorte del rostro
**Módulo:** `src/emova/core/vision/face_cropper.py`

Una vez extraídas y validadas matemáticamente las coordenadas del bounding box, se descarta el fondo y el contexto, manteniendo exclusivamente los pixeles faciales mediante "slicing" (rebanado) bidimensional de arreglos NumPy.

```python
def crop_face(frame, box):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = box

    # Reglas de validación: Asegurar que los límites estén dentro del mapeo original de la imagen 
    # (Evita IndexError por desbordamiento de matrices si el rostro está en el filo de la cámara)
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    # Rebanar y devolver la matriz que incluye estrictamente el Bounding Box (Y: Alto, X: Ancho)
    face = frame[y1:y2, x1:x2]
    return face
```

---

## 4.7.5 Redimensionamiento
**Módulo:** `src/emova/core/vision/preprocess.py`

Justificado por el análisis de métodos de la Tabla 44, se redimensiona por **Interpolación Bilineal**. A diferencia del cálculo de píxel vecino (nearest-neighbor), la interpolación bilineal evalúa los 4 vecinos colindantes para suavizar colores. Su propósito es anclar la resolución a `$224 \times 224$`, ya que las arquitecturas modernas como ResNet-50 están preentrenadas sobre ImageNet y exigen rigurosamente esta resolución temporal. 

```python
import cv2

def preprocess(image):
    # Interpolación Bilineal a 224x224 pixeles (cv2.INTER_LINEAR)
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)
    return image
```

---

## 4.7.6 Normalización
**Módulo:** `src/emova/core/vision/preprocess.py` (continuación de la función previa)

Para mantener la estabilidad funcional (Transfer Learning), los tensores de PyTorch exigen estandarización por Z-Score (Canalización). Además, OpenCV trabaja por defecto las matrices del color en orden **BGR** de forma inversa a PyTorch (**RGB**). 

```python
import cv2
import numpy as np

def preprocess(image):
    # 1. Redimensionamiento
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)

    # 2. Re-alinear el orden de color de BGR oficial de OpenCV hacia RGB universal
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 3. Flotar y escalar los pixeles de byte (0-255) a distribución (0.0-1.0)
    image = image.astype(np.float32) / 255.0
    
    # Valores estadísticos pre-calculados del set oficial de ImageNet (μ, σ)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)  
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    # 4. Normalización Estadística Estandarizada Z-score: z = (x - μ) / σ
    # Se aplica vía broadcasting subyacente de C en NumPy 
    image = (image - mean) / std

    # 5. Estandarización de Capas para PyTorch
    # Reordenar ejes de "Height-Width-Channel" (HWC) a "Channel-Height-Width" (CHW)
    image = np.transpose(image, (2, 0, 1))

    return image
```

Con este Tensor final procesado (una estructura matricial validada de forma de bloque `[3, 224, 224]`), la canalización envía el dato directo a los módulos inferenciales de Machine Learning descartando ruido analítico por iluminación, borrosidad o desajuste jerárquico.
