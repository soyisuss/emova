"""
Módulo del Modelo de Tokens. Definición del payload JWT.
"""
from pydantic import BaseModel

class Token(BaseModel):
    """Respuesta estándar para una solicitud login exitosa OAUTH2."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Datos encriptados subyacentes transportados por el token (subject)."""
    email: str | None = None
