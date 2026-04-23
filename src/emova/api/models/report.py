"""
Pydantic models module for the Report entity.

Manages generated accesses to reports resulting from the CV system.
References a concluded session and links an external resource.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from emova.api.models.types import PyObjectId

class ReportBase(BaseModel):
    """Universal base for an associated report."""
    reportUrl: str = Field(..., description="Signed URL or relative Google Cloud Storage path")
    userId: PyObjectId = Field(..., description="Direct User reference for fast RBAC access control")
    testName: str = Field(default="Prueba General", description="Nombre o Identificador visible de la sesión de prueba")

class ReportCreate(ReportBase):
    """Schema for requesting new GCS Reports."""
    pass

class ReportUpdate(BaseModel):
    """Modification of metadata or expunged signed URL of the report."""
    reportUrl: Optional[str] = None
    userId: Optional[PyObjectId] = None

class ReportResponse(ReportBase):
    """Exposed Pydantic model returning control to the user querying this report."""
    id: PyObjectId = Field(alias="_id", description="MongoDB primary key index")
    createdAt: datetime = Field(description="Moment of analytical conclusion")

    model_config = ConfigDict(populate_by_name=True)

class ReportInDB(ReportBase):
    """Safeguarded in-database representation for concrete queries to the DB Engine."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
