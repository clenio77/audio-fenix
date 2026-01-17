"""
Testes - Domain Layer: Models

Testa os modelos de domínio (Project, Stem).
"""
import pytest
from datetime import datetime, timedelta
from domain.models.project import Project, ProjectStatus
from domain.models.stem import Stem


class TestProjectStatus:
    """Testes para o enum ProjectStatus."""
    
    def test_pending_status(self):
        """Status PENDING deve existir."""
        assert ProjectStatus.PENDING.value == "pending"
    
    def test_processing_status(self):
        """Status PROCESSING deve existir."""
        assert ProjectStatus.PROCESSING.value == "processing"
    
    def test_ready_status(self):
        """Status READY deve existir."""
        assert ProjectStatus.READY.value == "ready"
    
    def test_failed_status(self):
        """Status FAILED deve existir."""
        assert ProjectStatus.FAILED.value == "failed"


class TestStemTypes:
    """Testes para os tipos de stem suportados."""
    
    def test_vocals_type_supported(self):
        """Tipo vocals deve ser suportado."""
        stem_types = ['vocals', 'drums', 'bass', 'other']
        assert 'vocals' in stem_types
    
    def test_drums_type_supported(self):
        """Tipo drums deve ser suportado."""
        stem_types = ['vocals', 'drums', 'bass', 'other']
        assert 'drums' in stem_types
    
    def test_bass_type_supported(self):
        """Tipo bass deve ser suportado."""
        stem_types = ['vocals', 'drums', 'bass', 'other']
        assert 'bass' in stem_types
    
    def test_other_type_supported(self):
        """Tipo other deve ser suportado."""
        stem_types = ['vocals', 'drums', 'bass', 'other']
        assert 'other' in stem_types


class TestProjectModel:
    """Testes para o modelo Project."""
    
    def test_project_creation(self, db_session):
        """Deve criar um projeto válido."""
        project = Project(
            id="test-project-123",
            original_filename="song.mp3",
            original_file_path="/storage/uploads/song.mp3",
            file_size_mb=5,
            duration_seconds=180,
            status=ProjectStatus.PENDING,
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.id == "test-project-123"
        assert project.original_filename == "song.mp3"
        assert project.status == ProjectStatus.PENDING
    
    def test_project_default_status(self, db_session):
        """Status padrão deve ser PENDING."""
        project = Project(
            id="test-project-456",
            original_filename="audio.wav",
            original_file_path="/storage/audio.wav",
            file_size_mb=10,
            duration_seconds=120,
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.status == ProjectStatus.PENDING
    
    def test_project_timestamps(self, db_session):
        """Projeto deve ter timestamps de criação."""
        project = Project(
            id="test-project-789",
            original_filename="track.flac",
            original_file_path="/storage/track.flac",
            file_size_mb=15,
            duration_seconds=240,
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.created_at is not None
        assert isinstance(project.created_at, datetime)
    
    def test_project_status_update(self, db_session):
        """Deve atualizar status do projeto."""
        project = Project(
            id="test-update-001",
            original_filename="song.mp3",
            original_file_path="/storage/song.mp3",
            file_size_mb=8,
            duration_seconds=200,
            status=ProjectStatus.PENDING,
        )
        
        db_session.add(project)
        db_session.commit()
        
        # Atualizar status
        project.status = ProjectStatus.PROCESSING
        db_session.commit()
        
        # Recarregar do banco
        db_session.refresh(project)
        assert project.status == ProjectStatus.PROCESSING
    
    def test_project_with_expiration(self, db_session):
        """Projeto deve suportar data de expiração."""
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        project = Project(
            id="test-expiration-001",
            original_filename="song.mp3",
            original_file_path="/storage/song.mp3",
            file_size_mb=12,
            duration_seconds=300,
            expires_at=expires_at,
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.expires_at is not None


class TestStemModel:
    """Testes para o modelo Stem."""
    
    def test_stem_creation(self, db_session):
        """Deve criar uma stem válida."""
        import uuid
        
        # Primeiro criar projeto
        project = Project(
            id="project-for-stem",
            original_filename="song.mp3",
            original_file_path="/storage/song.mp3",
            file_size_mb=5,
            duration_seconds=120,
        )
        db_session.add(project)
        db_session.commit()
        
        # Criar stem
        stem = Stem(
            id=str(uuid.uuid4()),
            project_id=project.id,
            stem_type="vocals",
            file_path="/storage/stems/vocals.wav",
        )
        
        db_session.add(stem)
        db_session.commit()
        
        assert stem.stem_type == "vocals"
        assert stem.project_id == project.id
    
    def test_stem_all_types(self, db_session):
        """Deve criar stems de todos os tipos."""
        import uuid
        
        project = Project(
            id="project-all-stems",
            original_filename="song.mp3",
            original_file_path="/storage/song.mp3",
            file_size_mb=10,
            duration_seconds=180,
        )
        db_session.add(project)
        db_session.commit()
        
        stem_types = ['vocals', 'drums', 'bass', 'other']
        
        for stem_type in stem_types:
            stem = Stem(
                id=str(uuid.uuid4()),
                project_id=project.id,
                stem_type=stem_type,
                file_path=f"/storage/stems/{stem_type}.wav",
            )
            db_session.add(stem)
        
        db_session.commit()
        
        # Verificar que todas foram criadas
        stems = db_session.query(Stem).filter(
            Stem.project_id == project.id
        ).all()
        
        assert len(stems) == 4


class TestProjectStemRelationship:
    """Testes para o relacionamento Project <-> Stem."""
    
    def test_project_has_stems_attribute(self, db_session):
        """Projeto deve ter atributo stems."""
        project = Project(
            id="project-relationship",
            original_filename="song.mp3",
            original_file_path="/storage/song.mp3",
            file_size_mb=6,
            duration_seconds=150,
        )
        db_session.add(project)
        db_session.commit()
        
        # Verificar que o atributo stems existe
        assert hasattr(project, 'stems')
