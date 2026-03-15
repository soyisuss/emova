"""
Data Access Module using Motor and asynchronous injection.

Acts as a mediator with MongoDB for metadata, sessions, and document collections.
Provides lifespan calls (FastAPI start/close) for socket management.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from emova.api.core.config import settings

class Database:
    """Lightweight singleton class to inject its client from FastAPI."""
    client: AsyncIOMotorClient | None = None

db = Database()

async def get_database():
    """ 
    Dependency to inject into FastAPI routes for each http request
    to isolate and provide exclusive direct access to the `emova_db` database.
    """
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    """Called from `main.lifespan` at FastAPI startup. Executes TCP DB connection."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    """Closes the connection when finalizing the main framework session."""
    if db.client is not None:
        db.client.close()
