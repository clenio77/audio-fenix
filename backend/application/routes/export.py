"""
Export Route - Application Layer

Endpoint para exportar mix customizado.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import subprocess
import os
from datetime import datetime, timedelta

from domain.database import get_db_session
from domain.models.project import Project, ProjectStatus
from domain.models.stem import Stem
from application.schemas.project import ExportRequest, ExportResponse

router = APIRouter()


@router.post("/export", response_model=ExportResponse)
async def export_mix(
    request: ExportRequest,
    db: Session = Depends(get_db_session)
):
    """
    Exporta uma mixagem customizada baseada nos volumes e mutes configurados.
    
    Usa ffmpeg para combinar os stems com os volumes especificados.
    """
    # Buscar projeto
    project = db.query(Project).filter(Project.id == request.project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    if project.status != ProjectStatus.READY:
        raise HTTPException(status_code=400, detail="Projeto ainda não está pronto")
    
    # Buscar stems
    stems = db.query(Stem).filter(Stem.project_id == request.project_id).all()
    
    if not stems:
        raise HTTPException(status_code=404, detail="Stems não encontrados")
    
    # Preparar comando ffmpeg
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    exports_dir = storage_path / "exports" / request.project_id
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = f"mix_{request.project_id}.{request.format}"
    output_path = exports_dir / output_filename
    
    # Construir filtro de áudio do ffmpeg
    # Exemplo: -filter_complex "[0:a]volume=1.0[a0];[1:a]volume=0.5[a1];[a0][a1]amix=inputs=2"
    #
    # IMPORTANT: omit muted / zero-volume stems from amix inputs.
    # ffmpeg amix defaults to normalize=1 and scales by the count of *active*
    # inputs (by weight), not by audible amplitude. Feeding volume=0 silence
    # still counts as an active input and incorrectly attenuates the mix
    # (e.g. default muted click → quieter export; solo → ~1/N level).
    
    inputs = []
    filter_parts = []
    mix_inputs = []
    audible_count = 0
    
    for stem in stems:
        stem_type = stem.stem_type
        volume = request.volumes.get(stem_type, 1.0)
        is_muted = request.mutes.get(stem_type, False)
        
        if is_muted or volume <= 0:
            continue
        
        idx = audible_count
        inputs.extend(["-i", stem.file_path])
        filter_parts.append(f"[{idx}:a]volume={volume}[a{idx}]")
        mix_inputs.append(f"[a{idx}]")
        audible_count += 1
    
    if audible_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Nenhum stem audível para exportar (todos mutados ou volume zero)"
        )
    
    # Combinar todos os filtros
    filter_complex = ";".join(filter_parts)
    filter_complex += f";{''.join(mix_inputs)}amix=inputs={audible_count}:duration=longest[out]"
    
    # Comando ffmpeg
    cmd = [
        "ffmpeg",
        "-y",  # Sobrescrever arquivo existente
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ar", "44100",  # Sample rate
        "-ac", "2",  # Stereo
    ]
    
    # Adicionar codec baseado no formato
    if request.format == "mp3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
    elif request.format == "wav":
        cmd.extend(["-c:a", "pcm_s16le"])
    
    cmd.append(str(output_path))
    
    try:
        # Executar ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Erro ao exportar: {result.stderr}")
        
        # Calcular expiração (24h)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        return ExportResponse(
            download_url=f"/api/download/export/{request.project_id}/{output_filename}",
            expires_at=expires_at
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout ao exportar mix")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.get("/download/export/{project_id}/{filename}")
async def download_export(project_id: str, filename: str):
    """Download do arquivo exportado"""
    from fastapi.responses import FileResponse
    
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    file_path = storage_path / "exports" / project_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    )


@router.get("/download/{project_id}/{stem_type}")
async def download_stem(project_id: str, stem_type: str, db: Session = Depends(get_db_session)):
    """Download de um stem individual para streaming"""
    from fastapi.responses import FileResponse
    
    # Buscar stem no banco
    stem = db.query(Stem).filter(
        Stem.project_id == project_id,
        Stem.stem_type == stem_type
    ).first()
    
    if not stem:
        raise HTTPException(status_code=404, detail=f"Stem {stem_type} não encontrado")
    
    file_path = Path(stem.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=f"{stem_type}.wav",
        media_type="audio/wav"
    )
