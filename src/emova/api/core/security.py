"""
Módulo central de seguridad y encriptación (Argon2 / JWT).

Contiene los métodos para encriptar contraseñas.
Implementa requerimientos de confidencialidad y control de contraseñas.
"""
import secrets
import string
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional, Any
from jose import jwt

from emova.api.core.config import settings

# Se utiliza Argon2 de acuerdo con las mejores prácticas de hashing. 
# El algoritmo deprecated="auto" ayuda con transiciones de legado automáticas si es necesario.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Valida si una contraseña en texto plano coincide con su hash en la base de datos."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Realiza la función criptográfica Argon2 y retorna una cadena encriptada."""
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Construye un token JWT con tiempo de vida limitado.
    El sujeto (subject) normalmente es el correo del usuario.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_recovery_code(length: int = 6) -> str:
    """Genera un código aleatorio seguro para la recuperación de contraseña."""
    alphabet = string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
