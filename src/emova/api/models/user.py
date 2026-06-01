"""
Módulo de modelos Pydantic para la entidad Usuario.

Establece las reglas fundamentales y valida reglas de seguridad de contraseñas (RB9).
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re
from typing import Optional
from datetime import datetime
from emova.api.models.types import PyObjectId

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"

class UserBase(BaseModel):
    """Atributos intrínsecos de un usuario."""
    email: EmailStr = Field(..., description="Unique email address")

class UserCreate(UserBase):
    """Datos requeridos para registrar un usuario. Contiene la contraseña sin hash."""
    password: str = Field(..., description="Minimum 8 characters, 1 Uppercase, 1 Lowercase, 1 number, and 1 special character")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Aplica la regla de negocio RB9 para la seguridad de la contraseña en el registro."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres, 1 letra mayúscula, "
                "1 minúscula, 1 número y 1 carácter especial."
            )
        return v

class UserUpdatePassword(BaseModel):
    """DTO para el cambio seguro de contraseñas en el sistema DTO."""
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Aplica la regla de negocio RB9 para la seguridad durante el restablecimiento voluntario."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "La nueva contraseña debe tener al menos 8 caracteres, 1 letra mayúscula, "
                "1 minúscula, 1 número y 1 carácter especial."
            )
        return v

class UserUpdate(BaseModel):
    """Esquema para actualizaciones parciales del perfil."""
    email: Optional[EmailStr] = None

class ForgotPasswordRequest(BaseModel):
    """DTO para solicitar correo de restablecimiento de contraseña."""
    email: EmailStr = Field(..., description="Email address linked to the user account")

class ResetPasswordRequest(BaseModel):
    """DTO para cambiar contraseña mediante código de recuperación."""
    email: EmailStr = Field(..., description="Email address linked to the user account")
    code: str = Field(..., description="6-digit recovery code")
    new_password: str = Field(..., description="New requested password")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Aplica la regla de negocio RB9 para la seguridad durante el restablecimiento voluntario."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "The new password must have at least 8 characters, 1 uppercase letter, "
                "1 lowercase letter, 1 number, and 1 special character."
            )
        return v

class UserResponse(UserBase):
    """Vista expuesta externamente. Oculta de forma explícita la contraseña."""
    id: PyObjectId = Field(alias="_id", description="UUID for Mongo DB")

    model_config = ConfigDict(populate_by_name=True)

class UserInDB(UserBase):
    """Representación interna para MongoDB. Incluye la contraseña con hash."""
    passwordHash: str = Field(..., description="Password encrypted by Argon2/bcrypt")
    id: Optional[PyObjectId] = Field(None, alias="_id")
    recoveryCode: Optional[str] = Field(None, description="Recovery code for resetting password")
    recoveryCodeExpires: Optional[datetime] = Field(None, description="Expiration date for the recovery code")

    model_config = ConfigDict(populate_by_name=True)
