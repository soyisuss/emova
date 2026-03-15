"""
Módulo de rutas transaccionales para Evaluadores (Usuarios Sistema).

Gestiona de inicio a fin el ciclo de vida de una cuenta de usuario dentro del 
sistema: registro (RB9), consulta, actualización parcial, borrado y cambio de
contraseña segura (Argon2).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from emova.api.db.database import get_database
from emova.api.models.evaluador import (
    EvaluadorCreate,
    EvaluadorUpdate,
    EvaluadorUpdatePassword,
    EvaluadorResponse,
    EvaluadorInDB
)
from emova.api.core.security import get_password_hash, verify_password
from emova.api.routers.auth import get_current_evaluador

router = APIRouter(prefix="/evaluadores", tags=["Evaluadores (Usuarios)"])


@router.post("/", response_model=EvaluadorResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluador(
    evaluador: EvaluadorCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Registra y codifica la contraseña de manera segura."""
    existing_user = await db["evaluadores"].find_one({"correo": evaluador.correo})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo especificado ya se encuentra registrado."
        )

    evaluador_in_db = EvaluadorInDB(
        nombre=evaluador.nombre,
        correo=evaluador.correo,
        profesion=evaluador.profesion,
        contrasena=get_password_hash(evaluador.contrasena)
    )

    nuevo_doc = evaluador_in_db.model_dump(by_alias=True, exclude_none=True)
    resultado = await db["evaluadores"].insert_one(nuevo_doc)

    creado = await db["evaluadores"].find_one({"_id": resultado.inserted_id})
    return EvaluadorResponse(**creado)


@router.get("/me", response_model=EvaluadorResponse)
async def read_current_evaluador(
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador)
):
    """Obtiene los datos del propio usuario basándose en su JWT actvo."""
    return EvaluadorResponse(**current_evaluador.model_dump(by_alias=True))


@router.patch("/me", response_model=EvaluadorResponse)
async def update_current_evaluador(
    evaluador_in: EvaluadorUpdate,
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Edita atributos de la cuenta permitidos como profesion y correo."""
    update_data = evaluador_in.model_dump(exclude_unset=True)

    if "correo" in update_data and update_data["correo"] != current_evaluador.correo:
        existing_user = await db["evaluadores"].find_one({"correo": update_data["correo"]})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo introducido ya está tomado por otro usuario."
            )

    if update_data:
        await db["evaluadores"].update_one(
            {"_id": ObjectId(current_evaluador.id_evaluador)},
            {"$set": update_data}
        )

    actualizado = await db["evaluadores"].find_one({"_id": ObjectId(current_evaluador.id_evaluador)})
    return EvaluadorResponse(**actualizado)


@router.put("/me/password")
async def update_password(
    passwords: EvaluadorUpdatePassword,
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Cambia la constraseña requiriendo confirmación de la vieja (y validando RB9)."""
    if not verify_password(passwords.contrasena_antigua, current_evaluador.contrasena):
        raise HTTPException(
            status_code=400, detail="La contraseña actual proveída no es la correcta.")

    nueva_hashed = get_password_hash(passwords.contrasena_nueva)
    await db["evaluadores"].update_one(
        {"_id": ObjectId(current_evaluador.id_evaluador)},
        {"$set": {"contrasena": nueva_hashed}}
    )
    return {"message": "Contraseña actualizada exitosamente."}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_evaluador(
    current_evaluador: EvaluadorInDB = Depends(get_current_evaluador),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Borra la cuenta autenicada. Las tareas, proyectos asociados quedan huérfanos o en proceso de borrado cascada extra."""
    await db["evaluadores"].delete_one({"_id": ObjectId(current_evaluador.id_evaluador)})
    return None
