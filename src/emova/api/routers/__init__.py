"""
Initialization module to collect all application routers.
"""
from emova.api.routers import (
    auth, users, reports
)

__all__ = [
    "auth",
    "users",
    "reports"
]
