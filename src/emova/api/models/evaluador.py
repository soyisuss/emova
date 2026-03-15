"""
Módulo de modelos de Pydantic para la entidad Evaluador.

Establece las reglas fundamentales y los campos requeridos para un Evaluador (Usuario).
Valida las reglas de contraseñas complejas expuestas en (RB9).
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re
from typing import Optional
from emova.api.models.types import PyObjectId

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

class EvaluadorBase(BaseModel):
    """Atributos intrínsecos de un evaluador."""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre personal completo")
    correo: EmailStr = Field(..., description="Correo único")
    profesion: str = Field(..., min_length=2, max_length=100, description="Perfil profesional")

class EvaluadorCreate(EvaluadorBase):
    """Datos para registrar un Evaluador nuevo. Contiene la contraseña sin hash."""
    contrasena: str = Field(..., description="Mínimo 8 letras, 1 Mayus, 1 Minus, 1 num y 1 carác. especial")

    @field_validator("contrasena")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Aplica la regla de negocio RB9 para robustez de la contraseña al registrarse."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres, 1 mayúscula, "
                "1 minúscula, 1 número y 1 carácter especial."
            )
        return v

class EvaluadorUpdatePassword(BaseModel):
    """DTO para hacer el cambio seguro de contraseñas de Evaluadores en el sistema."""
    contrasena_antigua: str
    contrasena_nueva: str

    @field_validator("contrasena_nueva")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Aplica la regla de negocio RB9 de seguridad en el reseteo voluntario."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "La nueva contraseña debe tener al menos 8 caracteres, 1 mayúscula, "
                "1 minúscula, 1 número y 1 carácter especial."
            )
        return v

class EvaluadorUpdate(BaseModel):
    """Esquema para cambios parciales al perfil."""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    correo: Optional[EmailStr] = None
    profesion: Optional[str] = Field(None, min_length=2, max_length=100)

class EvaluadorResponse(EvaluadorBase):
    """Vista expuesta externamente al API. Oculta explícitamente la contraseña."""
    id_evaluador: PyObjectId = Field(alias="_id", description="UUID para BD Mongo")

    model_config = ConfigDict(populate_by_name=True)

class EvaluadorInDB(EvaluadorBase):
    """Representación interna exacta para MongoDB, incluye el password cifrado con hashing seguro."""
    contrasena: str = Field(..., description="Password criptografiado por Argon2/bcrypt")
    id_evaluador: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = ConfigDict(populate_by_name=True)
