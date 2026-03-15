"""
Transactional routes module for Users.

Manages the end-to-end lifecycle of a user account within the 
system: registration (RB9), querying, partial update, deletion, and 
secure password change (Argon2).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from emova.api.db.database import get_database
from emova.api.models.user import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserResponse,
    UserInDB
)
from emova.api.core.security import get_password_hash, verify_password
from emova.api.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Registers and securely encodes the password."""
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified email is already registered."
        )

    user_in_db = UserInDB(
        email=user.email,
        passwordHash=get_password_hash(user.passwordHash)
    )

    new_doc = user_in_db.model_dump(by_alias=True, exclude_none=True)
    result = await db["users"].insert_one(new_doc)

    created = await db["users"].find_one({"_id": result.inserted_id})
    return UserResponse(**created)


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: UserInDB = Depends(get_current_user)
):
    """Retrieves data of the own user based on the active JWT."""
    return UserResponse(**current_user.model_dump(by_alias=True))


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Edits permitted account attributes such as email."""
    update_data = user_in.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = await db["users"].find_one({"email": update_data["email"]})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The introduced email is already taken by another user."
            )

    if update_data:
        await db["users"].update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )

    updated = await db["users"].find_one({"_id": ObjectId(current_user.id)})
    return UserResponse(**updated)


@router.put("/me/password")
async def update_password(
    passwords: UserUpdatePassword,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Changes the password requiring confirmation of the old one (and validating RB9)."""
    if not verify_password(passwords.old_password, current_user.passwordHash):
        raise HTTPException(
            status_code=400, detail="The current password provided is incorrect.")

    new_hashed = get_password_hash(passwords.new_password)
    await db["users"].update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"passwordHash": new_hashed}}
    )
    return {"message": "Password updated successfully."}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Deletes the authenticated account."""
    await db["users"].delete_one({"_id": ObjectId(current_user.id)})
    return None
