"""
Database Configuration - Domain Layer

Configuração do SQLAlchemy e sessão de banco de dados.
Suporta SQLite (desenvolvimento) e PostgreSQL (produção).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from .models.base import Base

# URL do banco de dados
# Usar SQLite se não houver DATABASE_URL configurada
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/isomix.db")

# Configurar engine baseado no tipo de banco
if DATABASE_URL.startswith("sqlite"):
    # SQLite - configurações específicas
    os.makedirs("./data", exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite específico
    )
else:
    # PostgreSQL - configurações para produção
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa o banco de dados (cria tabelas)"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para obter uma sessão de banco de dados.
    
    Usage:
        with get_db() as db:
            project = db.query(Project).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Dependency para FastAPI.
    
    Usage:
        @app.get("/projects")
        def list_projects(db: Session = Depends(get_db_session)):
            return db.query(Project).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
