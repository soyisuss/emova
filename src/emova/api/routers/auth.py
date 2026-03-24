"""
Authentication and Authorization Module for Users.

Provides mechanisms for JWT (JSON Web Tokens) login and utilities 
for the safe extraction and injection of the authenticated user in other endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import JWTError, jwt

from emova.api.core.security import verify_password, create_access_token
from emova.api.core.config import settings
from emova.api.db.database import get_database
from emova.api.models.token import Token
from emova.api.models.user import UserInDB

# Oauth2 schema definition
# Assuming tokenUrl is the endpoint where the login form posts
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    """
    FastAPI dependency. Validates the provided JWT token and returns 
    the User credentials hosted in the database if everything is valid.
    
    Raises HTTPException if the token is invalid or the user no longer exists.
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
    Authenticates the user by validating their credentials (email and password).
    
    Returns a JWT access token upon success.
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
    
    # Create and return token (default expiration configured in settings)
    access_token = create_access_token(subject=user_db["email"])
    return {"access_token": access_token, "token_type": "bearer"}
