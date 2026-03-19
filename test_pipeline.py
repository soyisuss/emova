import os
import urllib.request
import cv2
import numpy as np

# Para asegurar que la ruta al módulo src/emova se encuentre en entornos que no están instalados por completo
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from emova.core.capture.camera import open_source, read_frame
from emova.core.vision.face_detector import FaceDetector
from emova.core.vision.pipeline import VideoPreprocessingPipeline

MODELS_DIR = "models"
# URLs oficiales del repositorio de OpenCV DNN_Samples para el detector SSD (ResNet)
PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel"
PROTO_PATH = os.path.join(MODELS_DIR, "deploy.prototxt")
MODEL_PATH = os.path.join(MODELS_DIR, "res10_300x300_ssd_iter_140000_fp16.caffemodel")

def download_models():
    """Descarga el prototxt y el caffemodel en caso de que no existan"""
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        
    if not os.path.exists(PROTO_PATH):
        print(f"Descargando {PROTO_PATH}...")
        urllib.request.urlretrieve(PROTO_URL, PROTO_PATH)
        
    if not os.path.exists(MODEL_PATH):
        print(f"Descargando {MODEL_PATH}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

def main():
    print("Verificando modelos de detección facial SSD ResNet-10...")
    download_models()
    
    print("Inicializando detector facial y VideoPreprocessingPipeline...")
    detector = FaceDetector(PROTO_PATH, MODEL_PATH)
    
    # Threshold de enfoque sugerido, puedes ajustarlo dependiendo de la cámara (por defecto es 80)
    pipeline = VideoPreprocessingPipeline(detector, focus_threshold=80.0)
    
    print("Abriendo la cámara web (presiona 'q' para salir)...")
    # 0 indica la cámara web instalada por defecto
    cap = open_source(0)
    
    while True:
        frame = read_frame(cap)
        if frame is None:
            break
            
        # Pasar el frame por el pipeline
        results = pipeline.process_frame(frame)
        
        # Visualizar usando OpenCV, así que copiamos el original
        display_frame = frame.copy()
        
        if len(results) == 0:
            # Si results está vacío, no pasó el filtro de enfoque o no se detectaron rostros
            cv2.putText(display_frame, "Buscando rostros / Desenfocado", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            for result in results:
                x1, y1, x2, y2 = result['box']
                score = result['focus_score']
                tensor = result['face_tensor']
                
                # Dibujar el Bounding Box de la cara
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Mostrar Varianza Laplaciana (Score de enfoque)
                info = f"Enfoque: {score:.1f}"
                cv2.putText(display_frame, info, (x1, y1 - 25), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Mostrar el formato final del Tensor para PyTorch -> shape usual (3, 224, 224)
                shape_info = f"Tensor: {tensor.shape}"
                cv2.putText(display_frame, shape_info, (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                # --- NUEVO: Mostrar la imagen procesada ---
                # El tensor tiene forma (3, 224, 224) y está en RGB. Lo pasamos a (224, 224, 3) (HWC)
                debug_face = np.transpose(tensor, (1, 2, 0))
                
                # Deshacer la normalización de ImageNet: (img * std) + mean
                mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                debug_face = (debug_face * std) + mean
                
                # Escalar de regreso a pixeles de 0 a 255
                debug_face = np.clip(debug_face * 255.0, 0, 255).astype(np.uint8)
                
                # PyTorch estaba en RGB, pero OpenCV renderiza en BGR, así que invertimos el color de nuevo
                debug_face = cv2.cvtColor(debug_face, cv2.COLOR_RGB2BGR)
                
                cv2.imshow("Rostro Preprocesado (Tensor a Píxel)", debug_face)

        cv2.imshow("EMOVA - Prueba de Preprocesamiento", display_frame)
        
        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Limpieza
    cap.release()
    cv2.destroyAllWindows()
    print("Cámara cerrada y liberada.")

if __name__ == "__main__":
    main()
