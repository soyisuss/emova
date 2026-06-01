"""
Módulo de acceso a datos utilizando Motor e inyección asíncrona.

Actúa como mediador con MongoDB para metadatos, sesiones y colecciones.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from emova.api.core.config import settings

class Database:
    """Clase Singleton ligera para inyectar su cliente desde FastAPI."""
    client: AsyncIOMotorClient | None = None

db = Database()

async def get_database():
    """ 
    Dependencia para inyectar en las rutas de FastAPI para cada petición HTTP
    y proveer acceso a la base de datos `emova_db`.
    """
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    """Se ejecuta en el inicio de la aplicación. Realiza la conexión TCP a la base de datos."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    """Cierra la conexión al finalizar la sesión del servidor."""
    if db.client is not None:
        db.client.close()
