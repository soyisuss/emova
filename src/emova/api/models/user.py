"""
Pydantic models module for the User entity.

Establishes fundamental rules and required fields for a User.
Validates complex password rules defined in (RB9).
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re
from typing import Optional
from emova.api.models.types import PyObjectId

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"

class UserBase(BaseModel):
    """Intrinsic attributes of a user."""
    email: EmailStr = Field(..., description="Unique email address")

class UserCreate(UserBase):
    """Data required to register a new User. Contains the unhashed password."""
    password: str = Field(..., description="Minimum 8 characters, 1 Uppercase, 1 Lowercase, 1 number, and 1 special character")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Applies business rule RB9 for password strength upon registration."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "The password must have at least 8 characters, 1 uppercase letter, "
                "1 lowercase letter, 1 number, and 1 special character."
            )
        return v

class UserUpdatePassword(BaseModel):
    """DTO for securely changing User passwords in the system."""
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Applies business rule RB9 for security during voluntary reset."""
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "The new password must have at least 8 characters, 1 uppercase letter, "
                "1 lowercase letter, 1 number, and 1 special character."
            )
        return v

class UserUpdate(BaseModel):
    """Schema for partial profile updates."""
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    """View exposed externally to the API. Explicitly hides the password."""
    id: PyObjectId = Field(alias="_id", description="UUID for Mongo DB")

    model_config = ConfigDict(populate_by_name=True)

class UserInDB(UserBase):
    """Exact internal representation for MongoDB, includes safely hashed password."""
    passwordHash: str = Field(..., description="Password encrypted by Argon2/bcrypt")
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = ConfigDict(populate_by_name=True)
