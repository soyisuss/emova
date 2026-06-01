"""
Módulo para el registro local de las emociones detectadas en formato CSV.
"""
import csv
import os

def save_emotion(task, emotion):
    """
    Guarda de forma persistente la emoción detectada para una tarea en un archivo CSV local.
    """
    # Crea el directorio de salidas si no existe
    os.makedirs("outputs", exist_ok=True)

    # Abre el archivo en modo anexar (append)
    with open("outputs/emotions.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([task, emotion])