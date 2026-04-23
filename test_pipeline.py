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
from emova.core.vision.emotion_model import EmotionRecognizer

MODELS_DIR = "models"
# URLs oficiales del repositorio de OpenCV DNN_Samples para el detector SSD (ResNet)
PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel"
PROTO_PATH = os.path.join(MODELS_DIR, "deploy.prototxt")
MODEL_PATH = os.path.join(MODELS_DIR, "res10_300x300_ssd_iter_140000_fp16.caffemodel")
EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "resnet50_emotion.onnx")

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

def find_available_cameras(max_tested=5):
    available_cameras = []
    print("\nBuscando cámaras disponibles... (esto puede tardar unos segundos)")
    for i in range(max_tested):
        # Usamos CAP_DSHOW en Windows para una apertura rápida, o apertura por defecto
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

def main():
    print("Verificando modelos de detección facial SSD ResNet-10...")
    download_models()
    
    print("Inicializando detector facial y VideoPreprocessingPipeline...")
    detector = FaceDetector(PROTO_PATH, MODEL_PATH)
    
    # Threshold de enfoque sugerido, puedes ajustarlo dependiendo de la cámara (por defecto es 80)
    pipeline = VideoPreprocessingPipeline(detector, focus_threshold=80.0)
    
    # --- INTERVENCIÓN: Instanciamos el modelo de emoción ---
    print("Iniciando EmotionRecognizer (Modelo ONNX)...")
    if not os.path.exists(EMOTION_MODEL_PATH):
        print(f"¡ADVERTENCIA! No se encontró el modelo {EMOTION_MODEL_PATH}")
        emotion_recognizer = None
    else:
        # Se asume Negativo, Neutral, Positivo por las 3 clases arrojadas por la red.
        emotion_recognizer = EmotionRecognizer(EMOTION_MODEL_PATH, labels=["Negativo", "Neutral", "Positivo"])
    
    cameras = find_available_cameras()
    if not cameras:
        print("No se encontraron cámaras conectadas que devuelvan imagen.")
        cam_idx = 0
    else:
        print("\n=== CÁMARAS ENCONTRADAS ===")
        for cam in cameras:
            print(f"[{cam}] Cámara {cam}")
        
        while True:
            try:
                choice = input(f"\nIngresa el número de la cámara a usar (por defecto {cameras[0]}): ")
                if choice.strip() == "":
                    cam_idx = cameras[0]
                    break
                cam_idx = int(choice)
                break
            except ValueError:
                print("Entrada inválida. Ingresa un número.")
    
    print(f"\nAbriendo la cámara {cam_idx} (presiona 'q' en la ventana para salir)...")
    cap = open_source(cam_idx)
    
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
                
                info_y_offset = 25
                # Mostrar Varianza Laplaciana (Score de enfoque)
                info = f"Enfoque: {score:.1f}"
                cv2.putText(display_frame, info, (x1, y1 - info_y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                info_y_offset += 25
                
                # --- NUEVO: Predicción de la emoción ---
                if emotion_recognizer:
                    emocion, confidencia, _ = emotion_recognizer.predict(tensor)
                    
                    # Decidimos color basado en la emoción (opcional)
                    if emocion == "Positivo": color = (0, 255, 255) # Amarillo
                    elif emocion == "Negativo": color = (0, 0, 255) # Rojo
                    else: color = (255, 255, 255) # Blanco (Neutral)
                        
                    texto_emo = f"Emocion: {emocion} ({confidencia*100:.1f}%)"
                    cv2.putText(display_frame, texto_emo, (x1, y1 - info_y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    info_y_offset += 25

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
