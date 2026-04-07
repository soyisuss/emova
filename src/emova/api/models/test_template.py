from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from emova.api.models.types import PyObjectId

class TestTask(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Description or instruction of the task")

class TestTemplateBase(BaseModel):
    test_id: str = Field(default="", description="Unique test ID like PU-01")
    name: str = Field(default="Configuración de Prueba", description="Optional name for the template")
    tasks: List[TestTask] = Field(..., description="List of tasks in this test configuration")

class TestTemplateCreate(TestTemplateBase):
    pass

class TestTemplateResponse(TestTemplateBase):
    id: PyObjectId = Field(alias="_id", description="MongoDB primary key")
    createdAt: datetime = Field(description="Creation time of the template")
    
    model_config = ConfigDict(populate_by_name=True)

class TestTemplateInDB(TestTemplateBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
