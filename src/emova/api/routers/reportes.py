"""
Módulo de rutas para la gestión y creación de Reportes.

Guarda persistencia referencial a los archivos de reporte alojados
físicamente en GCS y es relacionado directamente por la Sesion.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List

from emova.api.db.database import get_database
from emova.api.models.reporte import ReporteCreate, ReporteResponse, ReporteInDB
from emova.api.models.evaluador import EvaluadorInDB
from emova.api.routers.auth import get_current_evaluador

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("/", response_model=ReporteResponse, status_code=status.HTTP_201_CREATED)
async def create_reporte(
    reporte: ReporteCreate,
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Crea la ficha del reporte apuntando a sus rutas físicas/GCS."""
    # Ensure the reporte is created for the current evaluator
    if str(reporte.id_evaluador) != str(current_evaluador.id_evaluador):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear un reporte para otro evaluador."
        )

    nuevo_reporte = ReporteInDB(**reporte.model_dump())
    
    doc = nuevo_reporte.model_dump(by_alias=True, exclude_none=True)
    resultado = await db["reportes"].insert_one(doc)
    
    creado = await db["reportes"].find_one({"_id": resultado.inserted_id})
    return ReporteResponse(**creado)

@router.get("/", response_model=List[ReporteResponse])
async def list_reportes(
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Enlista todos los reportes historicos relacionados a las sesiones de este evaluador."""
    cursor = db["reportes"].find({"id_evaluador": str(current_evaluador.id_evaluador)})
    reportes = await cursor.to_list(length=200)
    return [ReporteResponse(**r) for r in reportes]

@router.get("/{id_reporte}", response_model=ReporteResponse)
async def read_reporte(
    id_reporte: str,
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Recauda el URL firmado para compartir de un ID concreto."""
    try:
         obj_id = ObjectId(id_reporte)
    except Exception:
         raise HTTPException(400, "Formato ID inválido")
         
    reporte = await db["reportes"].find_one({"_id": obj_id})
    if not reporte or str(reporte.get("id_evaluador")) != str(current_evaluador.id_evaluador):
        raise HTTPException(status_code=404, detail="El reporte no existe o no se tiene acceso resguardado.")
    
    return ReporteResponse(**reporte)

@router.delete("/{id_reporte}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reporte(
    id_reporte: str,
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Borra el link o URL. Típicamente no remueve GCS localmente aquí (delegado al file-manager)."""
    try:
         obj_id = ObjectId(id_reporte)
    except Exception:
         raise HTTPException(400, "Formato ID inválido")
         
    existente = await db["reportes"].find_one({"_id": obj_id})
    if not existente or str(existente.get("id_evaluador")) != str(current_evaluador.id_evaluador):
        raise HTTPException(status_code=404, detail="El reporte no existe.")
        
    await db["reportes"].delete_one({"_id": obj_id})
    return None
