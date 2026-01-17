"""
Domain Models - Package Initialization

Expondo todos os modelos para facilitar imports e garantir
que o SQLAlchemy carregue todos os relacionamentos corretamente.
"""
from .base import Base
from .project import Project, ProjectStatus
from .stem import Stem
from .user import User, UserPlan

__all__ = [
    "Base",
    "Project",
    "ProjectStatus",
    "Stem",
    "User",
    "UserPlan",
]

