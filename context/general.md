# Consideraciones Técnicas y Guía de Desarrollo (Emova)

Este documento centraliza los lineamientos técnicos y reglas de negocio críticas a considerar durante el desarrollo de nuevas features.

## 1. Arquitectura y Estándares de Código
- **Arquitectura Modular por Capas:** El sistema debe mantener un diseño desacoplado separando claramente la Capa Local de los Servicios Remotos para garantizar la mantenibilidad y escalabilidad.
- **Cumplimiento de PEP8:** Todo el código escrito en Python debe seguir estrictamente este estándar de estilo.
- **Documentación Interna:** Es obligatorio el uso de docstrings en módulos, clases y funciones para asegurar al menos un **70% de mantenibilidad documentada**.
- **Pruebas Automatizadas (RNF6):** Cada nueva feature debe incluir sus respectivas pruebas unitarias y de integración.

## 2. Procesamiento de IA y Visión por Computadora
- **Pipeline de Inferencia:** El modelo estándar elegido es **ResNet-50**.
- **Preprocesamiento de Imágenes:** Cualquier ajuste debe respetar:
  - **Dimensiones de Entrada:** Redimensionamiento a `224x224` píxeles empleando interpolación bilineal.
  - **Normalización:** Se deben aplicar los valores estadísticos de ImageNet: `μ = [0.485, 0.456, 0.406]` y `σ = [0.229, 0.224, 0.225]`.
- **Restricción de FPS (RNF10):** El sistema debe procesar **exactamente 3 fotogramas por segundo (fps)** de video para el análisis emocional.
- **Categorías de Emoción (RB7):** Los algoritmos de clasificación deben limitarse **estrictamente a tres estados**: Contento, Descontento y Neutral.

## 3. Seguridad y Privacidad (Crítico)
- **Privacidad del Usuario (RNF8):** El sistema **NO debe almacenar los videos de los rostros** de los participantes bajo ninguna circunstancia. Sólo se perciste y almacena el resultado final del análisis (emoción a través del tiempo).
- **Manejo de Credenciales (RNF12):** Está estrictamente prohibido el almacenamiento de contraseñas en texto plano. Se debe usar el proceso de hashing definido en el proyecto (**Argon2**).
- **Gestión de Entornos (Secretos):** Es **crítico** utilizar un archivo `.env` para almacenar cualquier credencial (bases de datos, claves de GCS, etc). Estos archivos **NUNCA** deben subirse al repositorio de código (asegurarse de que estén en el `.gitignore`).
- **Política de Contraseñas (RB9):** Cualquier flujo de registro o cambio de contraseña debe validar los siguientes requisitos:
  - Mínimo de 8 caracteres.
  - Al menos una letra mayúscula y una letra minúscula.
  - Al menos un número.
  - Al menos un carácter especial (ej. `!@#$%^&*`).

## 4. Gestión de Datos y Persistencia
- **Modelo Híbrido de Almacenamiento:**
  - **MongoDB:** Destinado únicamente para almacenar metadatos, configuraciones de sesiones, URLs o rutas firmadas de los reportes.
  - **Google Cloud Storage (GCS):** Utilizado exclusivamente para el almacenamiento físico de los reportes PDF generados u otros artefactos pesados permitidos.
- **Reglas de Eliminación (RB5):** No se debe permitir la eliminación de tareas que ya cuenten con una sesión de prueba realizada asociada para mantener consistencia de datos históricos.

## 5. Interfaz y UX (RNF11)
Cualquier propuesta o componente de interfaz desarrollado en **PySide6** (o cualquier framework UI) debe cumplir rigurosamente con los siguientes estándares de accesibilidad:
- **Tamaño de letra mínimo:** 10.5 pt.
- **Contraste visual mínimo:** Ratio de 4.5:1.
- **Áreas clicables:** Área interactiva mínima de `44 x 44` px.
- **Espaciado:** Mínimo de `8 px` entre controles interactivos consecutivos para evitar clicks accidentales.

## 6. Herramientas y Versionamiento
- **Gestión de Dependencias:** Se debe priorizar y utilizar estrictamente **`uv`** (y el archivo `pyproject.toml`) para el manejo de dependencias de Python y mantener el proyecto sincronizado de forma rápida y confiable. Se desaconseja el uso de `pip install` directo.
- **Convención de Commits:** El repositorio emplea [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) para el historial de control de versiones. Todo mensaje de commit debe seguir esta convención (ejemplo: `feat: agrega validación de contraseñas`, `fix: corrige error de importación relativa`).


## 7. Adicional
- **Idioma:** Todo el codigo que se escriba, asi como nombres de archivos, nombres de funciones etc. debe de estar en ingles. 