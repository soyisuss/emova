# Roadmap y Pendientes de Implementación: Proyecto EMOVA

A continuación, se detallan las características que todavía no han sido implementadas en el proyecto y el orden recomendado para lograr la entrega final basada en la revisión del código actual.

## 🔴 Features Faltantes 

### 1. Inferencia Core de Inteligencia Artificial (ONNX)
Actualmente, el motor de análisis visual ya cuenta con el Pipeline de Preprocesamiento (`test_pipeline.py`, `pipeline.py` y detección facial SSD), pero el clasificador principal de emociones es un *"mock"* (datos simulados y aleatorios).
- Reemplazar la simulación en `emotion_predictor.py` para instanciar una sesión ONNX (`onnxruntime-gpu`) alojando ResNet-50.
- Lógica real para convertir el tensor de (3, 224, 224) extraído por el pipeline en la inferencia de emociones (Contento, Neutral, Descontento).

### 2. Capa Cliente hacia la API (Integración PySide6)
La interfaz de usuario está bastante avanzada visualmente y posee flujos completos de vistas (`QStackedWidget`), pero opera aislada de los datos del servidor.
- Instalar e incorporar `httpx` o usar `requests`.
- Desarrollar las rutinas HTTP cliente que se comuniquen con `/auth/login`, `/users/`, y `/tests/templates/` rellenando de forma asincrónica de la UI (para no trabar el main thread de PySide).

### 3. Completitud del CRUD de Dominio y Participantes
Si bien recientemente se integraron a la API los `TestTemplates` (rutas para configuración de tareas/tests), aún faltan entidades exigidas.
- Faltan CRUD de **Participantes** (`participants.py`) en bases de datos (MongoDB).
- Faltan Endpoints para **Sesión de Prueba**, integrando grabaciones, tareas analizadas y el reporte emocional general.

### 4. Integración Cloud y Privacidad de Datos (GCS)
- No hay integración oficial en el código con **Google Cloud Storage (GCS)**, aun cuando el paquete está instalado.
- Se está guardando un archivo local crudo temporal para pruebas en `storage/emotion_logger.py` (`outputs/emotions.csv`), y esto rompe la privacidad y Regímenes No Funcionales (RNF8). El flujo de stream de datos debe derivarse íntegramente a memoria sin tocar disco local de cara a GCS.
- Generación de *firmas URLs* (Signed URLs) de Cloud Storage para compartir los accesos desde la API.

### 5. Reportes Analíticos 
La estructura del reporte `ReportLab` ya está generada y compila correctamente un PDF base. Sin embargo, no hay análisis numérico sobre este.
- Integrar `matplotlib` para inyectar gráficos de área y líneas que muestren la evolución emocional de un usuario sobre el documento PDF.

### 6. Pruebas Unitarias e Integración
- No hay tests automatizados a nivel API ni a nivel IA Core. La carpeta `/tests/` carece de integración real (como Pytest) para asegurar que todo el sistema sea resistente a regresiones.

### 7. Infraestructura (Docker)
- Creación de un `.Dockerfile` robusto y un posible `docker-compose.yml` para garantizar desplegabilidad en producción de forma agnóstica.

---

## 📈 Recomendación del Orden de Implementación

Para asegurar que EMOVA se ensamble de manera iterativa sin cuellos de botella cruzados, sugiero este orden de desarrollo:

### Fase 1: Motor Real de Inteligencia (Backbone IA)
**Target:** Finalizar el sistema de inferencia usando ONNX. 
**Justificación:** EMOVA provee valor principalmente a través del análisis emocional. Acoplar la inferencia real de `ResNet-50` desde ONNXRuntime con el nuevo pipeline logrará consolidar la base de la App de Escritorio.

### Fase 2: Consolidar la API Rest y MongoDB (Dominio Complementario)
**Target:** Terminar el CRUD (Participantes, Sesiones Reales en Vivo).
**Justificación:** El Desktop App no podrá mandar a guardar ninguna sesión evaluada (de IA de Fase 1) si la Base de Datos y la API no poseen un router o modelo de "SesionPrueba" capaz de recibir el metadata.

### Fase 3: Integración del GUI Desktop Client a la API
**Target:** Acoplar PySide6 y la API.
**Justificación:** Habiendo API con Auth y Endpoints de Sesión lista, las peticiones HTTPS desde el Cliente Desktop pueden programarse. El *Login*, el Fetching de Dashboards y el envío remoto pueden enlazarse.

### Fase 4: Cloud Storage, Documentos y Reglas de Privacidad (GCS y PDF)
**Target:** Carga segura de CSV/PDFs a GCS y Generación gráfica con ReportLab + Matplotlib.
**Justificación:** Toda la sesión visual ya se simula remota, por lo que acá se inscribe y sella la confidencialidad subiéndolo vía stream hacia Google Cloud con Reportes Gráficos listos para el cliente.

### Fase 5: Aseguramiento de Calidad y Refactorización (QA / Devops)
**Target:** Pytest, Dockerización.
**Justificación:** Finalizamos enrutando el sistema mediante un setup robusto. Producir el aislamiento de componentes validarán ante pruebas unitarias e integrales que la arquitectura general no sea endeble a errores del usuario u OOM de la IA.
