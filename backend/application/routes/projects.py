"""
Projects Routes - Application Layer

Endpoints para gerenciamento de projetos do usuário.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from domain.database import get_db_session
from domain.models.project import Project, ProjectStatus
from application.routes.auth import get_current_user, require_user
from domain.models.user import User

router = APIRouter()


# ===============================
# Schemas
# ===============================

from pydantic import BaseModel

class StemResponse(BaseModel):
    """Schema de resposta para uma stem."""
    id: str
    type: str
    url: str
    
    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """Schema para item na lista de projetos."""
    id: str
    original_filename: str
    status: str
    progress: int = 0
    created_at: datetime
    duration_seconds: Optional[int] = None
    file_size_mb: int
    
    class Config:
        from_attributes = True


class ProjectDetail(BaseModel):
    """Schema para detalhes completos do projeto."""
    id: str
    original_filename: str
    status: str
    progress: int = 0
    message: str = ""
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    file_size_mb: int
    ai_model: Optional[str] = None
    stems: List[StemResponse] = []
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema para resposta de lista de projetos."""
    projects: List[ProjectListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


# ===============================
# Endpoints
# ===============================

@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=50, description="Itens por página"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db_session)
):
    """
    Lista projetos do usuário autenticado.
    
    - **page**: Número da página (começa em 1)
    - **page_size**: Quantidade de itens por página (máximo 50)
    - **status_filter**: Filtrar por status (pending, processing, ready, failed)
    
    Retorna lista paginada com metadados.
    """
    # Query base
    query = db.query(Project).filter(Project.user_id == user.id)
    
    # Filtro de status
    if status_filter:
        try:
            status_enum = ProjectStatus(status_filter)
            query = query.filter(Project.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido: {status_filter}"
            )
    
    # Contagem total
    total = query.count()
    
    # Ordenação e paginação
    offset = (page - 1) * page_size
    projects = query.order_by(desc(Project.created_at)).offset(offset).limit(page_size).all()
    
    # Montar resposta
    project_list = []
    for project in projects:
        project_list.append(ProjectListItem(
            id=project.id,
            original_filename=project.original_filename,
            status=project.status.value,
            progress=getattr(project, 'progress', 0) or 0,
            created_at=project.created_at,
            duration_seconds=project.duration_seconds,
            file_size_mb=project.file_size_mb,
        ))
    
    return ProjectListResponse(
        projects=project_list,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(projects)) < total,
    )


@router.get("/projects/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db_session)
):
    """
    Busca detalhes de um projeto específico.
    
    Retorna informações completas incluindo stems processados.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Montar stems
    stems = []
    if project.stems:
        for stem in project.stems:
            stems.append(StemResponse(
                id=stem.id,
                type=stem.stem_type,
                url=f"/api/stems/{stem.id}/download",
            ))
    
    return ProjectDetail(
        id=project.id,
        original_filename=project.original_filename,
        status=project.status.value,
        progress=getattr(project, 'progress', 0) or 0,
        message=getattr(project, 'message', '') or '',
        error=project.error_message,
        created_at=project.created_at,
        updated_at=project.updated_at,
        expires_at=project.expires_at,
        duration_seconds=project.duration_seconds,
        file_size_mb=project.file_size_mb,
        ai_model=project.ai_model,
        stems=stems,
    )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db_session)
):
    """
    Exclui um projeto do usuário.
    
    Também remove os arquivos de áudio associados.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # TODO: Remover arquivos físicos do storage
    
    # Remover do banco
    db.delete(project)
    db.commit()
    
    return {
        "success": True,
        "message": "Projeto excluído com sucesso"
    }


@router.get("/projects/stats/summary")
async def get_projects_stats(
    user: User = Depends(require_user),
    db: Session = Depends(get_db_session)
):
    """
    Retorna estatísticas dos projetos do usuário.
    """
    total = db.query(Project).filter(Project.user_id == user.id).count()
    
    ready = db.query(Project).filter(
        Project.user_id == user.id,
        Project.status == ProjectStatus.READY
    ).count()
    
    processing = db.query(Project).filter(
        Project.user_id == user.id,
        Project.status == ProjectStatus.PROCESSING
    ).count()
    
    failed = db.query(Project).filter(
        Project.user_id == user.id,
        Project.status == ProjectStatus.FAILED
    ).count()
    
    return {
        "total": total,
        "ready": ready,
        "processing": processing,
        "failed": failed,
        "pending": total - ready - processing - failed,
    }
