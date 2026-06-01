"""
Módulo de modelos Pydantic para la entidad Reporte.

Administra las referencias de acceso a reportes generados.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from emova.api.models.types import PyObjectId

class ReportBase(BaseModel):
    """Base universal para un reporte asociado."""
    reportUrl: str = Field(..., description="Signed URL or relative Google Cloud Storage path")
    userId: PyObjectId = Field(..., description="Direct User reference for fast RBAC access control")
    testName: str = Field(default="Prueba General", description="Nombre o Identificador visible de la sesión de prueba")

class ReportCreate(ReportBase):
    """Esquema para solicitar nuevos reportes en GCS."""
    pass

class ReportUpdate(BaseModel):
    """Esquema para modificación de metadatos del reporte."""
    reportUrl: Optional[str] = None
    userId: Optional[PyObjectId] = None

class ReportResponse(ReportBase):
    """Modelo Pydantic expuesto para el usuario que consulta el reporte."""
    id: PyObjectId = Field(alias="_id", description="MongoDB primary key index")
    createdAt: datetime = Field(description="Moment of analytical conclusion")

    model_config = ConfigDict(populate_by_name=True)

class ReportInDB(ReportBase):
    """Representación interna en base de datos para consultas directas."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
