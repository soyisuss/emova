"""
Módulo de modelos de Pydantic para la entidad Reporte.

Maneja los accesos generados hacia reportes resultantes del sistema de CV. 
Referencia una sesión culminada y liga un recurso externo.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from emova.api.models.types import PyObjectId

class ReporteBase(BaseModel):
    """Base universal para un reporte asociado a sesión."""
    url: str = Field(..., description="URL firmada o ruta relativa de Google Cloud Storage")
    id_evaluador: PyObjectId = Field(..., description="Referencia a Evaluador directo para control de acceso RBAC rápido")

class ReporteCreate(ReporteBase):
    """Esquema de solicitud de Alta a Reportes de GCS."""
    pass

class ReporteUpdate(BaseModel):
    """Modificación de metadatos o URL firmada expungida del reporte."""
    url: Optional[str] = None
    id_evaluador: Optional[PyObjectId] = None

class ReporteResponse(ReporteBase):
    """Pydantic expuesto que devuelve el control al evaluador que pregunta por este reporte."""
    id_reporte: PyObjectId = Field(alias="_id", description="Index llave principal de Mongo")
    fecha_creacion: datetime = Field(description="Momento de conclusión analítica de la sesión")

    model_config = ConfigDict(populate_by_name=True)

class ReporteInDB(ReporteBase):
    """Forma in-database resguadada para queries concretos a Motor BD."""
    id_reporte: Optional[PyObjectId] = Field(None, alias="_id")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
