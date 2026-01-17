"""
Stem Model - Domain Layer

Entidade que representa uma faixa de áudio separada (stem).
"""
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class Stem(Base):
    """
    Faixa de áudio separada (stem).
    
    Cada projeto gera 4 stems: vocals, drums, bass, other
    """
    __tablename__ = "stems"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Tipo de stem (vocals, drums, bass, other)
    stem_type = Column(String, nullable=False)
    
    # Caminho do arquivo
    file_path = Column(String, nullable=False)
    file_size_mb = Column(Integer, nullable=True)
    
    # Relacionamentos
    project = relationship("Project", back_populates="stems")
    
    def __repr__(self):
        return f"<Stem {self.stem_type} - Project {self.project_id}>"
