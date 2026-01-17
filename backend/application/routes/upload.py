"""
Upload Route - Application Layer

Endpoint para upload de arquivos de áudio.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import os
from datetime import datetime, timedelta

from domain.database import get_db_session
from domain.models.project import Project, ProjectStatus
from domain.validators.audio import AudioValidator
from business.usage_limiter import UsageLimiter, SubscriptionPlan
from model.tasks import process_audio
from application.schemas.project import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    """
    Upload de arquivo de áudio para processamento.
    
    - Valida formato e tamanho
    - Salva arquivo temporário
    - Cria projeto no banco
    - Enfileira tarefa de processamento
    """
    try:
        # TODO: Obter plano do usuário (por enquanto, usar Free)
        user_plan = SubscriptionPlan.FREE
        limiter = UsageLimiter(user_plan)
        
        # Salvar arquivo temporariamente para validação
        storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
        uploads_dir = storage_path / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        project_id = str(uuid.uuid4())
        temp_file_path = uploads_dir / project_id / file.filename
        temp_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Obter tamanho do arquivo
        file_size_bytes = temp_file_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Validar formato
        is_valid, error_msg = AudioValidator.validate_format(temp_file_path)
        if not is_valid:
            temp_file_path.unlink()  # Deletar arquivo inválido
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Obter metadados
        metadata = AudioValidator.get_audio_metadata(temp_file_path)
        duration_seconds = metadata.get("duration_seconds", 0)
        duration_minutes = duration_seconds / 60
        
        # Validar tamanho
        can_upload, error_msg = limiter.can_upload(file_size_mb, duration_minutes)
        if not can_upload:
            temp_file_path.unlink()
            raise HTTPException(status_code=400, detail=error_msg)
        
        # TODO: Verificar cota diária
        # uploads_today = db.query(Project).filter(...).count()
        # has_quota, error_msg = limiter.check_daily_quota(uploads_today)
        
        # Criar projeto no banco
        retention_hours = limiter.get_retention_hours()
        expires_at = datetime.utcnow() + timedelta(hours=retention_hours)
        
        project = Project(
            id=project_id,
            original_filename=file.filename,
            original_file_path=str(temp_file_path),
            file_size_mb=int(file_size_mb),
            duration_seconds=int(duration_seconds),
            status=ProjectStatus.PENDING,
            expires_at=expires_at,
        )
        
        db.add(project)
        db.commit()
        
        # Enfileirar tarefa de processamento
        task = process_audio.delay(project_id, str(temp_file_path))
        
        return UploadResponse(
            project_id=project_id,
            status=ProjectStatus.PENDING,
            message="Upload realizado com sucesso. Processamento iniciado."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")
