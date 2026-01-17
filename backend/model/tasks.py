"""
Celery Tasks - Model Layer

Tarefas assíncronas para processamento de áudio.
"""
import sys
import os

# Adicionar /app ao path para encontrar módulos
sys.path.insert(0, '/app')

import logging
from pathlib import Path
from typing import Dict

from .worker import celery_app
from .demucs_engine import create_separator
from .separator import StemType

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="model.tasks.process_audio")
def process_audio(self, project_id: str, input_file_path: str) -> Dict[str, str]:
    """
    Tarefa Celery para processar áudio e gerar stems.
    
    Args:
        project_id: ID único do projeto
        input_file_path: Caminho do arquivo de áudio original
        
    Returns:
        Dicionário com caminhos dos stems gerados
        
    Raises:
        Exception: Se houver erro no processamento
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from domain.models.project import Project, ProjectStatus
    from domain.models.stem import Stem
    
    # Criar sessão do banco
    database_url = os.getenv("DATABASE_URL", "postgresql://isomix_user:isomix_pass@db:5432/isomix")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        logger.info(f"[Task {self.request.id}] Iniciando processamento do projeto {project_id}")
        print(f"🎵 Iniciando processamento do projeto {project_id}")
        
        # Atualizar status para PROCESSING no banco
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = ProjectStatus.PROCESSING
            db.commit()
            print(f"📊 Status atualizado para PROCESSING")
        
        # Atualizar estado Celery
        self.update_state(state="PROCESSING", meta={"progress": 0, "status": "Iniciando..."})
        
        # Criar separador
        model_type = os.getenv("AI_MODEL", "demucs")
        separator = create_separator(model_type)
        
        # Definir diretório de saída
        storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
        output_dir = storage_path / "stems" / project_id
        
        # Atualizar progresso
        self.update_state(state="PROCESSING", meta={"progress": 10, "status": "Separando áudio..."})
        
        # Executar separação
        input_path = Path(input_file_path)
        print(f"🎵 Iniciando separação: {input_path} -> {output_dir}")
        stems = separator.separate(input_path, output_dir)
        
        # Converter Path para string
        stems_dict = {stem_type.value: str(stem_path) for stem_type, stem_path in stems.items()}
        
        logger.info(f"[Task {self.request.id}] Processamento concluído: {len(stems_dict)} stems gerados")
        print(f"✅ {len(stems_dict)} stems gerados")
        
        # Detectar BPM e gerar click track
        self.update_state(state="PROCESSING", meta={"progress": 80, "status": "Detectando BPM..."})
        
        try:
            from .bpm_detector import bpm_detector
            
            click_track_path = output_dir / "click.wav"
            click_path, detected_bpm = bpm_detector.generate_click_track(
                audio_path=input_path,
                output_path=click_track_path
            )
            
            # Adicionar click track aos stems
            stems_dict["click"] = click_path
            print(f"🥁 Click track gerado com BPM: {detected_bpm}")
            
        except Exception as e:
            logger.warning(f"Falha ao gerar click track: {e}")
            print(f"⚠️ Click track não gerado: {e}")
            detected_bpm = None
        
        # Detectar acordes
        self.update_state(state="PROCESSING", meta={"progress": 90, "status": "Detectando acordes..."})
        
        detected_chords = []
        try:
            from .chord_detector import chord_detector
            
            chords_path = output_dir / "chords.json"
            detected_chords = chord_detector.detect_chords(input_path)
            chord_detector.save_chords(detected_chords, chords_path)
            print(f"🎸 {len(detected_chords)} acordes detectados")
            
        except Exception as e:
            logger.warning(f"Falha ao detectar acordes: {e}")
            print(f"⚠️ Acordes não detectados: {e}")
        
        # Salvar stems no banco de dados
        if project:
            import uuid
            for stem_type, stem_path in stems_dict.items():
                stem_file = Path(stem_path)
                stem_size = stem_file.stat().st_size / (1024 * 1024) if stem_file.exists() else 0
                
                stem = Stem(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    stem_type=stem_type,
                    file_path=stem_path,
                    file_size_mb=stem_size,
                )
                db.add(stem)
                print(f"💾 Stem salvo: {stem_type} ({stem_size:.2f} MB)")
            
            # Atualizar status do projeto para READY
            project.status = ProjectStatus.READY
            db.commit()
            print(f"✅ Status atualizado para READY")
        
        # Atualizar progresso final
        self.update_state(state="PROCESSING", meta={"progress": 100, "status": "Concluído!"})
        
        return {
            "project_id": project_id,
            "stems": stems_dict,
            "model_used": separator.get_model_name(),
            "bpm": detected_bpm,
        }
        
    except Exception as e:
        logger.exception(f"[Task {self.request.id}] Erro no processamento")
        print(f"❌ Erro: {str(e)}")
        
        # Atualizar status para FAILED
        if project:
            project.status = ProjectStatus.FAILED
            project.error_message = str(e)
            db.commit()
        
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
    finally:
        db.close()


@celery_app.task(name="model.tasks.cleanup_old_files")
def cleanup_old_files(retention_hours: int = 24):
    """
    Tarefa periódica para limpar arquivos antigos.
    
    Args:
        retention_hours: Tempo de retenção em horas
    """
    from datetime import datetime, timedelta
    import shutil
    
    logger.info(f"Iniciando limpeza de arquivos com mais de {retention_hours}h")
    
    storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
    cutoff_time = datetime.now() - timedelta(hours=retention_hours)
    
    deleted_count = 0
    
    for directory in ["uploads", "stems", "exports"]:
        dir_path = storage_path / directory
        
        if not dir_path.exists():
            continue
        
        for project_dir in dir_path.iterdir():
            if not project_dir.is_dir():
                continue
            
            # Verificar tempo de modificação
            mtime = datetime.fromtimestamp(project_dir.stat().st_mtime)
            
            if mtime < cutoff_time:
                logger.info(f"Deletando projeto antigo: {project_dir.name}")
                shutil.rmtree(project_dir)
                deleted_count += 1
    
    logger.info(f"Limpeza concluída: {deleted_count} projetos deletados")
    return {"deleted": deleted_count}
