"""
Routes module for Reports management and creation.

Maintains referential persistence to report files hosted
physically in GCS and is related directly by the Session.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List

from emova.api.db.database import get_database
from emova.api.models.report import ReportCreate, ReportResponse, ReportInDB
from emova.api.models.user import UserInDB
from emova.api.routers.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Creates the report record pointing to its physical/GCS paths."""
    # Ensure the report is created for the current user
    if str(report.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create a report for another user."
        )

    new_report = ReportInDB(**report.model_dump())
    
    doc = new_report.model_dump(by_alias=True, exclude_none=True)
    result = await db["reports"].insert_one(doc)
    
    created = await db["reports"].find_one({"_id": result.inserted_id})
    return ReportResponse(**created)

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Lists all historical reports related to this user."""
    cursor = db["reports"].find({"userId": str(current_user.id)})
    reports = await cursor.to_list(length=200)
    return [ReportResponse(**r) for r in reports]

@router.get("/{report_id}", response_model=ReportResponse)
async def read_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieves the signed URL to share from a concrete ID."""
    try:
         obj_id = ObjectId(report_id)
    except Exception:
         raise HTTPException(400, "Invalid ID format")
         
    report = await db["reports"].find_one({"_id": obj_id})
    if not report or str(report.get("userId")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="The report does not exist or you do not have safeguarded access.")
    
    return ReportResponse(**report)

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Deletes the link or URL. Typically does not remove from GCS locally here (delegated to file-manager)."""
    try:
         obj_id = ObjectId(report_id)
    except Exception:
         raise HTTPException(400, "Invalid ID format")
         
    existing = await db["reports"].find_one({"_id": obj_id})
    if not existing or str(existing.get("userId")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="The report does not exist.")
        
    await db["reports"].delete_one({"_id": obj_id})
    return None
