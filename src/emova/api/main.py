"""
Main module and entry point for the FastAPI application.

Configures initialization, database connections, and registers
each of the API modules (routers).
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from emova.api.core.config import settings
from emova.api.db.database import connect_to_mongo, close_mongo_connection
from emova.api.routers import (
    auth, users, reports
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Asynchronous handling of startup and shutdown components like the database."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Robust API for managing users and reports of the EMOVA system.",
    version="0.1.0",
    lifespan=lifespan
)

# Integration of routers separated by entity/domain
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router)


@app.get("/", tags=["Health"])
async def root():
    """Base route to verify that the core FastAPI server is operational."""
    return {"message": f"Service running: {settings.PROJECT_NAME}"}
