"""
Status Route - Application Layer

Endpoint para consultar status de processamento.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from domain.database import get_db_session
from domain.models.project import Project, ProjectStatus
from domain.models.stem import Stem
from application.schemas.project import ProjectStatusResponse, StemInfo
from model.worker import celery_app

router = APIRouter()


@router.get("/status/{project_id}", response_model=ProjectStatusResponse)
async def get_project_status(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Consulta o status de processamento de um projeto.
    
    Retorna:
    - Status atual (pending, processing, ready, failed)
    - Progresso (0-100%)
    - URLs dos stems (se pronto)
    - Mensagens de erro (se falhou)
    """
    # Buscar projeto no banco
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Verificar se expirou
    if project.is_expired():
        project.status = ProjectStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=410, detail="Projeto expirado")
    
    # Montar resposta baseada no status
    response = ProjectStatusResponse(
        project_id=project.id,
        status=project.status,
        progress=0,
        created_at=project.created_at,
    )
    
    if project.status == ProjectStatus.PENDING:
        response.progress = 0
        response.message = "Aguardando processamento..."
        
    elif project.status == ProjectStatus.PROCESSING:
        # Tentar obter progresso da tarefa Celery
        # TODO: Implementar tracking de progresso
        response.progress = 50
        response.message = "Processando áudio..."
        
    elif project.status == ProjectStatus.READY:
        response.progress = 100
        response.message = "Processamento concluído!"
        
        # Buscar stems
        stems = db.query(Stem).filter(Stem.project_id == project_id).all()
        response.stems = [
            StemInfo(
                type=stem.stem_type,
                url=f"/api/download/{project_id}/{stem.stem_type}",
                size_mb=stem.file_size_mb
            )
            for stem in stems
        ]
        
    elif project.status == ProjectStatus.FAILED:
        response.progress = 0
        response.error = project.error_message or "Erro desconhecido no processamento"
    
    return response


@router.get("/chords/{project_id}")
async def get_project_chords(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Retorna os acordes detectados de um projeto.
    
    Returns:
        Lista de acordes com {time, chord, confidence, duration}
    """
    import os
    import json
    from pathlib import Path
    
    # Buscar projeto
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    if project.status != ProjectStatus.READY:
        raise HTTPException(status_code=400, detail="Projeto ainda não está pronto")
    
    # Buscar arquivo de acordes
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    chords_path = storage_path / "stems" / project_id / "chords.json"
    
    if not chords_path.exists():
        # Se não encontrar direto, buscar em subpastas
        for subdir in (storage_path / "stems" / project_id).iterdir():
            if subdir.is_dir():
                alt_path = subdir / "chords.json"
                if alt_path.exists():
                    chords_path = alt_path
                    break
    
    if not chords_path.exists():
        return {"chords": [], "message": "Acordes não disponíveis para este projeto"}
    
    with open(chords_path, 'r', encoding='utf-8') as f:
        chords = json.load(f)
    
    return {"chords": chords, "count": len(chords)}


@router.get("/lyrics/{project_id}")
async def get_project_lyrics(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Retorna a letra transcrita de um projeto.
    
    Returns:
        Lista de frases com {start, end, text}
    """
    import os
    import json
    from pathlib import Path
    
    # Buscar projeto
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    if project.status != ProjectStatus.READY:
        raise HTTPException(status_code=400, detail="Projeto ainda não está pronto")
    
    # Buscar arquivo de letras
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    lyrics_path = storage_path / "stems" / project_id / "lyrics.json"
    
    if not lyrics_path.exists():
        # Tentar em subpastas caso o Demucs tenha criado uma
        for item in (storage_path / "stems" / project_id).iterdir():
            if item.is_dir():
                alt_path = item / "lyrics.json"
                if alt_path.exists():
                    lyrics_path = alt_path
                    break
    
    if not lyrics_path.exists():
        return {"lyrics": [], "message": "Letra não disponível para este projeto"}
    
    with open(lyrics_path, 'r', encoding='utf-8') as f:
        lyrics = json.load(f)
    
    return {"lyrics": lyrics, "count": len(lyrics)}
