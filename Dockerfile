# Usamos una imagen ligera de Python
FROM python:3.10-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos uv
RUN pip install uv

# Instalamos únicamente las dependencias de la API (evitamos PySide6 y modelos de visión pesados)
RUN uv pip install --system fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[argon2] python-multipart google-cloud-storage email-validator fastapi-mail

# Copiamos el __init__ principal para que Python reconozca a 'emova' como paquete
COPY src/emova/__init__.py ./src/emova/__init__.py
# Copiamos ÚNICAMENTE la carpeta de la API
COPY src/emova/api/ ./src/emova/api/

# Agregamos src al PYTHONPATH para que Python encuentre el módulo emova
ENV PYTHONPATH=/app/src

# Cloud Run escucha por defecto en el puerto 8080
ENV PORT=8080

# Comando para iniciar la API en modo producción (llamamos a fastapi directamente)
CMD ["fastapi", "run", "src/emova/api/main.py", "--port", "8080", "--host", "0.0.0.0"]
