"""
Módulo de rutas para la gestión y creación de reportes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List

from emova.api.db.database import get_database
from emova.api.models.report import ReportCreate, ReportResponse, ReportInDB
from emova.api.models.user import UserInDB
from emova.api.routers.auth import get_current_user
from emova.api.core.storage import StorageManager

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Crea el registro del reporte apuntando a sus rutas físicas de GCS."""
    # Asegurar que el reporte sea creado para el usuario actual
    if str(report.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear un reporte a nombre de otro usuario."
        )

    new_report = ReportInDB(**report.model_dump())
    
    doc = new_report.model_dump(by_alias=True, exclude_none=True)
    result = await db["reports"].insert_one(doc)
    
    created = await db["reports"].find_one({"_id": result.inserted_id})
    return ReportResponse(**created)

@router.post("/upload", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_create_report(
    file: UploadFile = File(...),
    testName: str = Form(default="Prueba General"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Sube un archivo PDF directamente a GCS y persiste la referencia."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo subido debe ser formato PDF.")
        
    try:
        content = await file.read()
        # Subida utilizando el StorageManager asíncrono
        url = await StorageManager.upload_report_pdf(content, str(current_user.id), file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo el archivo a GCS: {str(e)}")
        
    # Construyendo una simulación del payload para crear el reporte
    doc_payload = {
        "reportUrl": url,
        "userId": current_user.id,
        "testName": testName
    }
    new_report = ReportInDB(**doc_payload)
    
    db_doc = new_report.model_dump(by_alias=True, exclude_none=True)
    result = await db["reports"].insert_one(db_doc)
    
    created = await db["reports"].find_one({"_id": result.inserted_id})
    return ReportResponse(**created)

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Lista todos los reportes históricos del usuario."""
    cursor = db["reports"].find({"userId": str(current_user.id)})
    reports = await cursor.to_list(length=200)
    return [ReportResponse(**r) for r in reports]

@router.get("/{report_id}", response_model=ReportResponse)
async def read_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Recupera la URL firmada para compartir a partir de un ID concreto."""
    try:
         obj_id = ObjectId(report_id)
    except Exception:
         raise HTTPException(400, "El formato del identificador de reporte es inválido.")
         
    report = await db["reports"].find_one({"_id": obj_id})
    if not report or str(report.get("userId")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="El reporte no existe o no tienes los permisos de acceso requeridos.")
    
    return ReportResponse(**report)

@router.get("/{report_id}/download")
async def download_report_bytes(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Descarga los bytes crudos de GCS para omitir el error XML de buckets privados."""
    try:
         obj_id = ObjectId(report_id)
    except Exception:
         raise HTTPException(400, "El formato del identificador es inválido.")
         
    report = await db["reports"].find_one({"_id": obj_id})
    if not report or str(report.get("userId")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="El reporte no existe o no tienes los permisos.")
    
    try:
        pdf_bytes = await StorageManager.download_report_pdf(report.get("reportUrl"))
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f'attachment; filename="Reporte_{report_id}.pdf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error originando en GCS: {str(e)}")

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Elimina la referencia del reporte (no el archivo físico en GCS)."""
    try:
         obj_id = ObjectId(report_id)
    except Exception:
         raise HTTPException(400, "El formato del identificador de reporte es inválido.")
         
    existing = await db["reports"].find_one({"_id": obj_id})
    if not existing or str(existing.get("userId")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="El reporte solicitado no existe en el sistema.")
        
    await db["reports"].delete_one({"_id": obj_id})
    return None
