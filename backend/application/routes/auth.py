"""
Auth Routes - Application Layer

Endpoints de autenticação (registro, login, logout).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from domain.database import get_db_session
from domain.models.user import User
from domain.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from application.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    MessageResponse,
)

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ===============================
# Dependency: Current User
# ===============================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db_session)
) -> Optional[User]:
    """
    Dependency para obter o usuário atual a partir do token JWT.
    Retorna None se não autenticado (para rotas opcionais).
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    if not payload:
        return None
    
    if payload.get("type") != "access":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = AuthService.get_user_by_id(db, user_id)
    return user


async def require_user(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Dependency que EXIGE autenticação.
    Lança exceção se usuário não estiver autenticado.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    return user


# ===============================
# Endpoints
# ===============================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db_session)
):
    """
    Registra um novo usuário.
    
    - **email**: Email válido e único
    - **password**: Mínimo 6 caracteres
    - **name**: Nome do usuário (opcional)
    
    Retorna tokens JWT para autenticação imediata.
    """
    user, error = AuthService.register_user(
        db=db,
        email=request.email,
        password=request.password,
        name=request.name,
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    # Gerar tokens
    access_token = AuthService.create_access_token(user.id, user.email, user.plan)
    refresh_token = AuthService.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db_session)
):
    """
    Autentica um usuário existente.
    
    - **email**: Email cadastrado
    - **password**: Senha do usuário
    
    Retorna tokens JWT para autenticação.
    """
    user = AuthService.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gerar tokens
    access_token = AuthService.create_access_token(user.id, user.email, user.plan)
    refresh_token = AuthService.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db_session)
):
    """
    Renova o token de acesso usando o refresh token.
    
    - **refresh_token**: Token de refresh válido
    
    Retorna novos tokens JWT.
    """
    payload = AuthService.decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido ou expirado",
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    
    # Gerar novos tokens
    access_token = AuthService.create_access_token(user.id, user.email, user.plan)
    new_refresh_token = AuthService.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_user)):
    """
    Retorna os dados do usuário autenticado.
    
    Requer autenticação via Bearer token.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        plan=user.plan,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db_session)
):
    """
    Altera a senha do usuário autenticado.
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha (mínimo 6 caracteres)
    """
    success, error = AuthService.change_password(
        db=db,
        user=user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    return MessageResponse(
        success=True,
        message="Senha alterada com sucesso",
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(user: User = Depends(require_user)):
    """
    Realiza logout do usuário.
    
    Nota: Em implementação JWT stateless, o logout é feito no cliente
    removendo os tokens. Este endpoint serve para ações adicionais
    como invalidar refresh tokens em um blacklist (futuro).
    """
    # TODO: Adicionar token a blacklist para invalidação real
    return MessageResponse(
        success=True,
        message="Logout realizado com sucesso",
    )
