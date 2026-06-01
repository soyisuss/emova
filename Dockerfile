# Imagen ligera de Python
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Instalación de uv
RUN pip install uv

# Instalación de dependencias de la API
RUN uv pip install --system fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[argon2] python-multipart google-cloud-storage email-validator fastapi-mail

# Copia el __init__ principal
COPY src/emova/__init__.py ./src/emova/__init__.py

# Copia la carpeta de la API
COPY src/emova/api/ ./src/emova/api/

# Agrega src al PYTHONPATH
ENV PYTHONPATH=/app/src

# Cloud Run escucha por defecto en el puerto 8080
ENV PORT=8080

# Comando para iniciar la API en modo producción
CMD ["fastapi", "run", "src/emova/api/main.py", "--port", "8080", "--host", "0.0.0.0"]
