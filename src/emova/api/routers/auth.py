"""
Módulo de autenticación y autorización para usuarios.

Provee mecanismos de inicio de sesión JWT y utilidades de extracción del usuario.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import JWTError, jwt

from datetime import datetime, timedelta, timezone

from emova.api.core.security import verify_password, create_access_token, generate_recovery_code, get_password_hash
from emova.api.core.config import settings
from emova.api.db.database import get_database
from emova.api.models.token import Token
from emova.api.models.user import UserInDB, ForgotPasswordRequest, ResetPasswordRequest
from emova.api.core.email import send_recovery_email

# Definición de esquema OAuth2
# Asumiendo que tokenUrl es el endpoint donde se envía el formulario
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    """
    Dependencia de FastAPI. Valida el token JWT provisto y retorna
    las credenciales del usuario de la base de datos si es válido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar tus credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_db = await db["users"].find_one({"email": email})
    if user_db is None:
        raise credentials_exception
        
    return UserInDB(**user_db)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Autentica al usuario validando sus credenciales.
    Retorna un token de acceso JWT al tener éxito.
    """
    user_db = await db["users"].find_one({"email": form_data.username})
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user_db["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear y retornar el token JWT
    access_token = create_access_token(subject=user_db["email"])
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Inicia el proceso de recuperación de contraseña.
    Genera un código y lo envía al correo del usuario.
    """
    user_db = await db["users"].find_one({"email": request.email})
    
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El correo electrónico no está registrado. No se puede enviar el código."
        )
    
    # Generar código de recuperación
    code = generate_recovery_code()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Actualizar BD con el código y expiración
    await db["users"].update_one(
        {"email": request.email},
        {"$set": {"recoveryCode": code, "recoveryCodeExpires": expiration}}
    )
    
    # Enviar correo electrónico
    try:
        await send_recovery_email(request.email, code)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Evitar caída total, idealmente manejar log en este punto
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send recovery email. Error: {str(e)}"
        )

    return {"message": "If the email is registered, you will receive a recovery code."}

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Restablece la contraseña por el código de recuperación válido.
    """
    user_db = await db["users"].find_one({"email": request.email})
    
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code or email."
        )
    
    # Validar que el código exista en BD
    stored_code = user_db.get("recoveryCode")
    stored_expiration = user_db.get("recoveryCodeExpires")
    
    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recovery code."
        )
        
    # Validar expiración del código
    if stored_expiration:
        # Asegurar zona horaria UTC
        if stored_expiration.tzinfo is None:
            stored_expiration = stored_expiration.replace(tzinfo=timezone.utc)
            
        if datetime.now(timezone.utc) > stored_expiration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recovery code has expired."
            )
            
    # Éxito, aplicar hash a la nueva contraseña
    hashed_password = get_password_hash(request.new_password)
    
    # Actualizar BD y remover campos de recuperación
    await db["users"].update_one(
        {"email": request.email},
        {
            "$set": {"passwordHash": hashed_password},
            "$unset": {"recoveryCode": "", "recoveryCodeExpires": ""}
        }
    )
    
    return {"message": "Password reset successful."}
    
