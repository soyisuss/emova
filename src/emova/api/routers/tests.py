from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from emova.api.db.database import get_database
from emova.api.models.test_template import TestTemplateCreate, TestTemplateResponse, TestTemplateInDB

router = APIRouter(
    prefix="/tests/templates",
    tags=["Test Templates"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TestTemplateResponse, status_code=status.HTTP_200_OK)
async def create_test_template(template: TestTemplateCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Guarda una nueva configuración de prueba (plantilla) con sus tareas.
    """
    collection = db["test_templates"]
    
    # Prepara el modelo para base de datos
    db_template = TestTemplateInDB(**template.model_dump())
    new_template_dict = db_template.model_dump(by_alias=True, exclude_none=True)
    
    if template.test_id:
        existing = await collection.find_one({"test_id": template.test_id})
        if existing:
            await collection.update_one(
                {"test_id": template.test_id},
                {"$set": {"tasks": new_template_dict.get("tasks", []), "name": new_template_dict.get("name")}}
            )
            updated_template = await collection.find_one({"test_id": template.test_id})
            return TestTemplateResponse(**updated_template)
            
    result = await collection.insert_one(new_template_dict)
    
    # Recupera el documento recién insertado
    created_template = await collection.find_one({"_id": result.inserted_id})
    if not created_template:
        raise HTTPException(status_code=500, detail="Failed to create test template")
        
    return TestTemplateResponse(**created_template)

@router.get("/", response_model=List[TestTemplateResponse])
async def list_test_templates(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Obtiene todas las configuraciones de prueba guardadas, ordenadas por fecha de creación (las más recientes primero).
    """
    collection = db["test_templates"]
    templates_cursor = collection.find({}).sort("createdAt", -1)
    
    templates = []
    async for doc in templates_cursor:
        templates.append(TestTemplateResponse(**doc))
        
    return templates

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_template(template_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Elimina una configuración de prueba por su ID.
    """
    try:
        obj_id = ObjectId(template_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid object id format")
        
    collection = db["test_templates"]
    result = await collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
        
    return None
