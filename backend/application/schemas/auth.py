"""
Auth Schemas - Application Layer

Schemas Pydantic para autenticação.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ===============================
# Request Schemas
# ===============================

class RegisterRequest(BaseModel):
    """Schema para registro de usuário."""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")
    name: Optional[str] = Field(None, max_length=100, description="Nome do usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@exemplo.com",
                "password": "senhasegura123",
                "name": "João Silva"
            }
        }


class LoginRequest(BaseModel):
    """Schema para login de usuário."""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@exemplo.com",
                "password": "senhasegura123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema para alteração de senha."""
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=6, description="Nova senha (mínimo 6 caracteres)")


class RefreshTokenRequest(BaseModel):
    """Schema para refresh de token."""
    refresh_token: str = Field(..., description="Token de refresh")


# ===============================
# Response Schemas
# ===============================

class UserResponse(BaseModel):
    """Schema de resposta com dados do usuário."""
    id: str
    email: str
    name: Optional[str]
    plan: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema de resposta com tokens JWT."""
    access_token: str = Field(..., description="Token JWT de acesso")
    refresh_token: str = Field(..., description="Token JWT de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UserResponse = Field(..., description="Dados do usuário")


class AuthResponse(BaseModel):
    """Schema genérico de resposta de autenticação."""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class MessageResponse(BaseModel):
    """Schema simples de resposta com mensagem."""
    success: bool
    message: str
