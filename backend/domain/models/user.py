"""
User Model - Domain Layer

Entidade que representa um usuário do sistema.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import Base


class UserPlan(str, enum.Enum):
    """Planos de assinatura do usuário."""
    FREE = "free"
    PRO = "pro"


class User(Base):
    """
    Usuário do sistema IsoMix Studio.
    
    Attributes:
        id: UUID único do usuário
        email: Email do usuário (único)
        hashed_password: Senha hasheada
        name: Nome do usuário
        plan: Plano de assinatura (FREE ou PRO)
        is_active: Se o usuário está ativo
        is_verified: Se o email foi verificado
        created_at: Data de criação
        updated_at: Data de última atualização
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    
    # Plano de assinatura
    plan = Column(String, default=UserPlan.FREE.value, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Contadores
    uploads_today = Column(String, default="0", nullable=False)  # JSON: {"date": "2024-01-01", "count": 0}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relacionamentos
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_pro(self) -> bool:
        """Verifica se o usuário é Pro."""
        return self.plan == UserPlan.PRO.value
