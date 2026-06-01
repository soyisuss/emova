"""
Módulo principal y punto de entrada para la aplicación FastAPI.

Configura la inicialización, conexiones a la base de datos y registra
cada uno de los módulos de la API (enrutadores).
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from emova.api.core.config import settings
from emova.api.db.database import connect_to_mongo, close_mongo_connection
from emova.api.routers import (
    auth, users, reports, tests
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo asíncrono de los componentes de inicio y cierre, como la base de datos."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API robusta para la gestión de usuarios y reportes del sistema EMOVA.",
    version="0.1.0",
    lifespan=lifespan
)

# Integración de enrutadores separados por entidad/dominio
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(tests.router)


@app.get("/", tags=["Health"])
async def root():
    """Ruta base para verificar que el servidor central FastAPI está operativo."""
    return {"message": f"Servicio en ejecución: {settings.PROJECT_NAME}"}

