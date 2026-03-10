# EMOVA: Sistema de Apoyo al Análisis Emocional en Pruebas de Usabilidad

**EMOVA** es una solución de software diseñada para optimizar la evaluación de interfaces digitales mediante el reconocimiento automático de expresiones faciales. El sistema permite capturar y analizar las reacciones emocionales espontáneas de los usuarios durante la interacción con sitios web, complementando las técnicas tradicionales de usabilidad como encuestas y entrevistas.

## 🚀 Características Principales
* **Reconocimiento Facial (FER):** Identificación y clasificación de tres estados emocionales: **Contento, Descontento y Neutral**.
* **Análisis No Intrusivo:** Permite a los usuarios interactuar con la interfaz de forma natural mientras el sistema registra signos de frustración, placer o sorpresa.
* **Integración de Métricas:** Relaciona las emociones detectadas con tareas específicas y tiempos de ejecución.
* **Reportes Profesionales:** Generación de reportes en formato **PDF** para evaluadores y exportación de datos crudos en **CSV** para análisis estadístico.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python (Ecosistema robusto para IA y visión por computadora).
* **Interfaz Gráfica:** PySide6 (Qt for Python) para una GUI nativa y modular.
* **Inteligencia Artificial:** * **Arquitectura:** ResNet-50 (Seleccionada por su equilibrio entre precisión y latencia).
  * **Inferencia:** ONNX Runtime para una ejecución eficiente en CPU/GPU.
* **Persistencia:** * **MongoDB:** Gestión de metadatos de sesiones y reportes.
  * **Google Cloud Storage (GCS):** Almacenamiento escalable de reportes en la nube.

## 🏗️ Arquitectura
El sistema implementa una **Metodología en Espiral** y una arquitectura modular por capas para asegurar la mantenibilidad y escalabilidad del código.



1. **Capa Local:** Gestiona la captura de video (OpenCV), el preprocesamiento de fotogramas y la inferencia del modelo.
2. **Capa Remota:** Se encarga de la persistencia de datos y el acceso a reportes históricos mediante enlaces firmados.

## 📋 Instalación y Uso (con `uv`)
Este proyecto utiliza `uv` para una gestión de dependencias rápida y determinista.

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/emova.git](https://github.com/tu-usuario/emova.git)
   cd emova
   ```

2. Sincronizar el entorno e instalar dependencias:
   ```bash
   uv sync
   ```

3. Ejecutar la aplicación:
   ```bash
   uv run src/emova/main.py
   ```

## 🎯 **Criterios de Éxito y Calidad**
- **Precisión**: El sistema debe alcanzar al menos un 80% - 85% de exactitud en la detección de emociones.
- **Rendimiento**: Análisis constante de 3 fotogramas por segundo (FPS).
- **Seguridad**: Confidencialidad de datos y almacenamiento de contraseñas mediante hashing (no texto plano).

**Desarrollado por**: Caballero Chávez Yael Jesús & Domínguez Rendón Melissa.
**Institución**: Instituto Politécnico Nacional - Escuela Superior de Cómputo (ESCOM).