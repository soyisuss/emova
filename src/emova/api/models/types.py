"""
Módulo para tipos genéricos auxiliares definidos en Pydantic y Type Hinting.
"""
from typing import Annotated
from pydantic import BeforeValidator

# Definimos el tipo reutilizable para el ID de MongoDB (ObjectId)
# Annotated añade el validador estricto para lidiar con el string en Pydantic V2
PyObjectId = Annotated[str, BeforeValidator(str)]
