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

# Stems de áudio que o ffmpeg consegue mixar. MIDI/MusicXML são artefatos
# de transcrição e não podem ser passados como inputs de áudio.
AUDIO_STEM_TYPES = frozenset({"vocals", "drums", "bass", "other", "click"})

STEM_MEDIA_TYPES = {
    "midi": ("audio/midi", ".mid"),
    "score": ("application/vnd.recordare.musicxml+xml", ".musicxml"),
}


def _safe_storage_path(base: Path, *parts: str) -> Path:
    """Resolve um caminho sob base e rejeita path traversal."""
    for part in parts:
        if (
            not part
            or part in (".", "..")
            or "/" in part
            or "\\" in part
            or "\x00" in part
        ):
            raise HTTPException(status_code=400, detail="Caminho inválido")

    base_resolved = base.resolve()
    candidate = (base.joinpath(*parts)).resolve()
    if not (candidate == base_resolved or base_resolved in candidate.parents):
        raise HTTPException(status_code=400, detail="Caminho inválido")
    return candidate


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
    
    # Buscar apenas stems de áudio (ignorar midi/score e outros artefatos)
    stems = [
        stem
        for stem in db.query(Stem).filter(Stem.project_id == request.project_id).all()
        if stem.stem_type in AUDIO_STEM_TYPES
    ]
    
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
    
    inputs = []
    filter_parts = []
    mix_inputs = []
    
    for idx, stem in enumerate(stems):
        stem_type = stem.stem_type
        volume = request.volumes.get(stem_type, 1.0)
        is_muted = request.mutes.get(stem_type, False)
        
        # Se mutado, volume = 0
        if is_muted:
            volume = 0.0
        
        inputs.extend(["-i", stem.file_path])
        filter_parts.append(f"[{idx}:a]volume={volume}[a{idx}]")
        mix_inputs.append(f"[a{idx}]")
    
    # Combinar todos os filtros
    filter_complex = ";".join(filter_parts)
    filter_complex += f";{''.join(mix_inputs)}amix=inputs={len(stems)}:duration=longest[out]"
    
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
        
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout ao exportar mix")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.get("/download/export/{project_id}/{filename}")
async def download_export(project_id: str, filename: str):
    """Download do arquivo exportado"""
    from fastapi.responses import FileResponse
    
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    try:
        file_path = _safe_storage_path(storage_path, "exports", project_id, filename)
    except HTTPException:
        raise
    
    if not file_path.exists() or not file_path.is_file():
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

    media_type, extension = STEM_MEDIA_TYPES.get(stem_type, ("audio/wav", ".wav"))
    # Preferir extensão real do arquivo quando disponível
    actual_suffix = file_path.suffix or extension
    
    return FileResponse(
        path=file_path,
        filename=f"{stem_type}{actual_suffix}",
        media_type=media_type
    )
