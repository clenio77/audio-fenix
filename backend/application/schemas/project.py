"""
Pydantic Schemas - Application Layer

Modelos de request/response para a API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Status do projeto"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class UploadResponse(BaseModel):
    """Resposta do endpoint de upload"""
    project_id: str
    status: ProjectStatus
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Upload realizado com sucesso. Processamento iniciado."
            }
        }


class StemInfo(BaseModel):
    """Informações de um stem"""
    type: str = Field(..., description="Tipo do stem (vocals, drums, bass, other)")
    url: str = Field(..., description="URL para download do stem")
    size_mb: Optional[float] = None


class ProjectStatusResponse(BaseModel):
    """Resposta do endpoint de status"""
    project_id: str
    status: ProjectStatus
    progress: int = Field(..., ge=0, le=100, description="Progresso em %")
    message: Optional[str] = None
    error: Optional[str] = None
    stems: Optional[List[StemInfo]] = None
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "ready",
                "progress": 100,
                "message": "Processamento concluído",
                "stems": [
                    {"type": "vocals", "url": "/download/vocals.wav"},
                    {"type": "drums", "url": "/download/drums.wav"},
                    {"type": "bass", "url": "/download/bass.wav"},
                    {"type": "other", "url": "/download/other.wav"}
                ],
                "created_at": "2024-01-01T12:00:00"
            }
        }


class ExportRequest(BaseModel):
    """Request para exportar mix customizado"""
    project_id: str
    volumes: Dict[str, float] = Field(
        ..., 
        description="Volume de cada stem (0.0 a 1.0)",
        example={"vocals": 1.0, "drums": 0.5, "bass": 0.8, "other": 0.7}
    )
    mutes: Dict[str, bool] = Field(
        ...,
        description="Stems mutados",
        example={"vocals": False, "drums": True, "bass": False, "other": False}
    )
    format: str = Field("mp3", description="Formato de saída (mp3 ou wav)")


class ExportResponse(BaseModel):
    """Resposta do endpoint de export"""
    download_url: str
    expires_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "download_url": "/download/mix_550e8400.mp3",
                "expires_at": "2024-01-02T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Arquivo muito grande",
                "detail": "Limite: 20MB para plano Free"
            }
        }
