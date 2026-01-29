"""Password reset request/response schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.password_validator import PasswordValidator


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset"""
    email: EmailStr = Field(
        ...,
        description="Email address of the account to reset"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema for confirming a password reset with new password"""
    token: str = Field(
        ...,
        description="Password reset token from email",
        min_length=1
    )
    new_password: str = Field(
        ...,
        description="New password (must meet strength requirements)",
        min_length=8
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        PasswordValidator.validate_or_raise(v)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "3x7k9mQpR2nV8yB4cF6hJ1sL5tN0wPqE7uG2aD9zX5C",
                "new_password": "StrongPassword123!"
            }
        }


class PasswordResetResponse(BaseModel):
    """Standard response for password reset operations"""
    message: str = Field(
        ...,
        description="Success or error message"
    )
    success: bool = Field(
        ...,
        description="Whether the operation succeeded"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "If the email exists, a password reset link has been sent",
                "success": True
            }
        }


class PasswordRequirements(BaseModel):
    """Password requirements for display to users"""
    requirements: list[str] = Field(
        ...,
        description="List of password requirements"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "requirements": [
                    "At least 8 characters",
                    "At least one uppercase letter (A-Z)",
                    "At least one lowercase letter (a-z)",
                    "At least one digit (0-9)",
                    "At least one special character (!@#$%^&*...)"
                ]
            }
        }
