"""
Project Model - Domain Layer

Entidade que representa um projeto de separação de áudio.
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from .base import Base


class ProjectStatus(str, enum.Enum):
    """Status possíveis de um projeto"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


class Project(Base):
    """
    Projeto de separação de áudio.
    
    Representa uma sessão de trabalho do usuário, contendo
    o arquivo original e os stems gerados.
    """
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Dono do projeto (opcional para compatibilidade com uploads anônimos)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # Metadados do arquivo original
    original_filename = Column(String, nullable=False)
    original_file_path = Column(String, nullable=False)
    file_size_mb = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    
    # Status do processamento
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PENDING, nullable=False)
    error_message = Column(String, nullable=True)
    
    # Modelo de IA usado
    ai_model = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    stems = relationship("Stem", back_populates="project", cascade="all, delete-orphan")
    user = relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project {self.id} - {self.status}>"
    
    def is_expired(self) -> bool:
        """Verifica se o projeto expirou"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_be_processed(self) -> bool:
        """Verifica se o projeto pode ser processado"""
        return self.status == ProjectStatus.PENDING
