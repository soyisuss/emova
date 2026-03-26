"""
Authentication and Authorization Module for Users.

Provides mechanisms for JWT (JSON Web Tokens) login and utilities 
for the safe extraction and injection of the authenticated user in other endpoints.
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
        detail="Could not validate credentials",
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
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user_db["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create and return token (default expiration configured in settings)
    access_token = create_access_token(subject=user_db["email"])
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Initiates the password recovery process. 
    Generates a code and sends it to the user's email if they exist.
    """
    user_db = await db["users"].find_one({"email": request.email})
    
    # We always return 200 to prevent email enumeration attacks
    if not user_db:
        return {"message": "If the email is registered, you will receive a recovery code."}
    
    # Generate recovery code
    code = generate_recovery_code()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Update DB with code and expiration
    await db["users"].update_one(
        {"email": request.email},
        {"$set": {"recoveryCode": code, "recoveryCodeExpires": expiration}}
    )
    
    # Send email
    try:
        await send_recovery_email(request.email, code)
    except Exception:
        # Avoid crashing completely, but ideally handle log here
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send recovery email."
        )

    return {"message": "If the email is registered, you will receive a recovery code."}

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Resets the password completely given a valid recovery code for the given email.
    """
    user_db = await db["users"].find_one({"email": request.email})
    
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code or email."
        )
    
    # Validate code exists in DB
    stored_code = user_db.get("recoveryCode")
    stored_expiration = user_db.get("recoveryCodeExpires")
    
    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recovery code."
        )
        
    # Validation expiration
    if stored_expiration:
        # Ensure UTC timezone awareness if the DB retrieved it without it
        if stored_expiration.tzinfo is None:
            stored_expiration = stored_expiration.replace(tzinfo=timezone.utc)
            
        if datetime.now(timezone.utc) > stored_expiration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recovery code has expired."
            )
            
    # Success, hash new password
    hashed_password = get_password_hash(request.new_password)
    
    # Update DB and remove recovery fields
    await db["users"].update_one(
        {"email": request.email},
        {
            "$set": {"passwordHash": hashed_password},
            "$unset": {"recoveryCode": "", "recoveryCodeExpires": ""}
        }
    )
    
    return {"message": "Password reset successful."}
    
