"""
Testes - Celery process_audio task error handling
"""
from unittest.mock import MagicMock, patch

import pytest

from domain.models.project import Project, ProjectStatus
from model.separator import StemType


class _SessionFactory:
    """sessionmaker()-compatible factory that reuses the pytest session."""

    def __init__(self, session):
        self._session = session

    def __call__(self, *args, **kwargs):
        # process_audio calls db.close() in finally — keep the test session alive
        self._session.close = lambda: None
        return self._session


@pytest.fixture
def process_project(db_session, temp_dir, sample_audio_bytes):
    """Projeto PENDING com arquivo de entrada e stems wav mockáveis."""
    project_id = "33333333-3333-3333-3333-333333333333"
    input_path = temp_dir / "input.wav"
    input_path.write_bytes(sample_audio_bytes)

    stems_dir = temp_dir / "stems" / project_id
    stems_dir.mkdir(parents=True)
    stem_paths = {}
    for stem_type in ("vocals", "drums", "bass", "other"):
        path = stems_dir / f"{stem_type}.wav"
        path.write_bytes(sample_audio_bytes)
        stem_paths[stem_type] = path

    project = Project(
        id=project_id,
        original_filename="input.wav",
        original_file_path=str(input_path),
        file_size_mb=1,
        status=ProjectStatus.PENDING,
    )
    db_session.add(project)
    db_session.commit()

    return {
        "project_id": project_id,
        "input_path": input_path,
        "stem_paths": stem_paths,
        "temp_dir": temp_dir,
    }


class TestProcessAudioErrorHandling:
    """Garante que sucesso commitado não é revertido para FAILED."""

    def test_post_ready_exception_keeps_ready_status(
        self,
        db_session,
        db_engine,
        process_project,
        monkeypatch,
    ):
        """
        Se update_state falhar DEPOIS do commit READY (ex.: Redis),
        o projeto deve permanecer READY com stems acessíveis.
        """
        from model.tasks import process_audio

        project_id = process_project["project_id"]
        input_path = process_project["input_path"]
        stem_paths = process_project["stem_paths"]
        temp_dir = process_project["temp_dir"]

        monkeypatch.setenv("STORAGE_PATH", str(temp_dir))
        monkeypatch.setenv("AI_MODEL", "demucs")

        mock_separator = MagicMock()
        mock_separator.separate.return_value = {
            StemType.VOCALS: stem_paths["vocals"],
            StemType.DRUMS: stem_paths["drums"],
            StemType.BASS: stem_paths["bass"],
            StemType.OTHER: stem_paths["other"],
        }
        mock_separator.get_model_name.return_value = "demucs-htdemucs"

        def update_state_side_effect(*args, **kwargs):
            meta = kwargs.get("meta") or {}
            if meta.get("progress") == 100:
                raise ConnectionError("redis unavailable")

        # Optional AI side-paths (BPM/chords/score/lyrics) are try/except'd;
        # missing heavy deps simply skip those steps.
        with patch("sqlalchemy.create_engine", return_value=db_engine), \
             patch("sqlalchemy.orm.sessionmaker", return_value=_SessionFactory(db_session)), \
             patch("model.tasks.create_separator", return_value=mock_separator), \
             patch.object(process_audio, "update_state", side_effect=update_state_side_effect):

            with pytest.raises(ConnectionError, match="redis unavailable"):
                process_audio.run(project_id, str(input_path))

        db_session.expire_all()
        project = db_session.query(Project).filter(Project.id == project_id).first()
        assert project is not None
        assert project.status == ProjectStatus.READY
        assert project.error_message is None
        assert len(project.stems) == 4

    def test_mid_processing_exception_marks_failed(
        self,
        db_session,
        db_engine,
        process_project,
        monkeypatch,
    ):
        """Falhas reais antes de READY ainda devem marcar FAILED."""
        from model.tasks import process_audio

        project_id = process_project["project_id"]
        input_path = process_project["input_path"]
        temp_dir = process_project["temp_dir"]

        monkeypatch.setenv("STORAGE_PATH", str(temp_dir))
        monkeypatch.setenv("AI_MODEL", "demucs")

        mock_separator = MagicMock()
        mock_separator.separate.side_effect = RuntimeError("demucs crashed")

        with patch("sqlalchemy.create_engine", return_value=db_engine), \
             patch("sqlalchemy.orm.sessionmaker", return_value=_SessionFactory(db_session)), \
             patch("model.tasks.create_separator", return_value=mock_separator), \
             patch.object(process_audio, "update_state", MagicMock()):

            with pytest.raises(RuntimeError, match="demucs crashed"):
                process_audio.run(project_id, str(input_path))

        db_session.expire_all()
        project = db_session.query(Project).filter(Project.id == project_id).first()
        assert project is not None
        assert project.status == ProjectStatus.FAILED
        assert "demucs crashed" in (project.error_message or "")
