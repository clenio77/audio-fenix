"""
Testes - Application Layer: API Endpoints

Testa os endpoints da API REST.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Testes para endpoints de saúde da API."""
    
    def test_root_endpoint(self, client: TestClient):
        """Endpoint raiz deve retornar informações do serviço."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "IsoMix Studio API"
        assert data["status"] == "running"
        assert "version" in data
    
    def test_health_endpoint(self, client: TestClient):
        """Endpoint /health deve retornar status healthy."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestUploadEndpoint:
    """Testes para o endpoint /api/upload."""
    
    def test_upload_without_file(self, client: TestClient):
        """Upload sem arquivo deve retornar erro 422."""
        response = client.post("/api/upload")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_upload_empty_file(self, client: TestClient):
        """Upload de arquivo vazio deve ser rejeitado."""
        response = client.post(
            "/api/upload",
            files={"file": ("empty.mp3", b"", "audio/mpeg")}
        )
        
        # Arquivo vazio será rejeitado
        assert response.status_code in [400, 422]
    
    @patch('model.tasks.process_audio.delay')
    @patch('domain.validators.audio.AudioValidator.validate_format')
    @patch('domain.validators.audio.AudioValidator.get_audio_metadata')
    def test_upload_valid_file(
        self,
        mock_metadata,
        mock_validate,
        mock_celery,
        client: TestClient,
        sample_audio_bytes
    ):
        """Upload de arquivo válido deve retornar 200 e project_id."""
        # Configurar mocks
        mock_validate.return_value = (True, None)
        mock_metadata.return_value = {
            "duration_seconds": 180,
            "sample_rate": 44100,
            "channels": 2
        }
        mock_celery.return_value = MagicMock(id="mock-task-id")
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.wav", sample_audio_bytes, "audio/wav")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert data["status"] == "pending"
        assert "message" in data
    
    @patch('domain.validators.audio.AudioValidator.validate_format')
    def test_upload_invalid_format(
        self,
        mock_validate,
        client: TestClient
    ):
        """Upload de formato inválido deve retornar erro 400."""
        mock_validate.return_value = (False, "Formato não suportado")
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", b"not audio content", "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @patch('model.tasks.process_audio.delay')
    @patch('domain.validators.audio.AudioValidator.validate_format')
    @patch('domain.validators.audio.AudioValidator.get_audio_metadata')
    def test_upload_file_too_large(
        self,
        mock_metadata,
        mock_validate,
        mock_celery,
        client: TestClient
    ):
        """Upload de arquivo muito grande deve retornar erro 400."""
        mock_validate.return_value = (True, None)
        mock_metadata.return_value = {
            "duration_seconds": 180,  # 3 minutos
            "sample_rate": 44100,
            "channels": 2
        }
        
        # Criar "arquivo" de 25MB (acima do limite FREE de 20MB)
        large_content = b"x" * (25 * 1024 * 1024)
        
        response = client.post(
            "/api/upload",
            files={"file": ("large.mp3", large_content, "audio/mpeg")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        # Mensagem deve indicar limite de tamanho
        assert "20MB" in data["detail"] or "grande" in data["detail"].lower()


class TestStatusEndpoint:
    """Testes para o endpoint /api/status/{project_id}."""
    
    def test_status_nonexistent_project(self, client: TestClient):
        """Consulta de projeto inexistente deve retornar 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(f"/api/status/{fake_id}")
        
        assert response.status_code == 404
    
    def test_status_invalid_uuid(self, client: TestClient):
        """Consulta com UUID inválido deve retornar erro."""
        response = client.get("/api/status/not-a-valid-uuid")
        
        # Pode ser 404 ou 422 dependendo da validação
        assert response.status_code in [404, 422]


class TestExportEndpoint:
    """Testes para o endpoint /api/export."""
    
    def test_export_without_project_id(self, client: TestClient):
        """Export sem project_id deve retornar erro."""
        response = client.post("/api/export", json={})
        
        assert response.status_code == 422  # Falta parâmetro obrigatório
    
    def test_export_nonexistent_project(self, client: TestClient):
        """Export de projeto inexistente deve retornar 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.post(
            "/api/export",
            json={
                "project_id": fake_id,
                "volumes": {"vocals": 1.0, "drums": 0.8},
                "mutes": {},
            }
        )
        
        assert response.status_code == 404

    def test_export_skips_non_audio_stems(
        self,
        client: TestClient,
        db_session,
        sample_audio_bytes,
        temp_dir,
    ):
        """
        MIDI/MusicXML não podem ir para o ffmpeg.
        Após a feature de partitura, esses artefatos são salvos como stems
        e quebravam o export se fossem misturados com áudio.
        """
        import uuid
        from unittest.mock import patch, MagicMock
        from domain.models.project import Project, ProjectStatus
        from domain.models.stem import Stem

        project_id = str(uuid.uuid4())
        vocals_path = temp_dir / "vocals.wav"
        midi_path = temp_dir / "song_transcription.mid"
        score_path = temp_dir / "song_score.musicxml"
        vocals_path.write_bytes(sample_audio_bytes)
        midi_path.write_text("not-audio")
        score_path.write_text("<score/>")

        project = Project(
            id=project_id,
            original_filename="song.mp3",
            original_file_path=str(temp_dir / "song.mp3"),
            file_size_mb=1,
            duration_seconds=10,
            status=ProjectStatus.READY,
        )
        db_session.add(project)
        db_session.add_all([
            Stem(
                id=str(uuid.uuid4()),
                project_id=project_id,
                stem_type="vocals",
                file_path=str(vocals_path),
                file_size_mb=0.1,
            ),
            Stem(
                id=str(uuid.uuid4()),
                project_id=project_id,
                stem_type="midi",
                file_path=str(midi_path),
                file_size_mb=0.01,
            ),
            Stem(
                id=str(uuid.uuid4()),
                project_id=project_id,
                stem_type="score",
                file_path=str(score_path),
                file_size_mb=0.01,
            ),
        ])
        db_session.commit()

        mock_result = MagicMock(returncode=0, stderr="")
        with patch("application.routes.export.subprocess.run", return_value=mock_result) as mock_run:
            response = client.post(
                "/api/export",
                json={
                    "project_id": project_id,
                    "volumes": {"vocals": 1.0, "midi": 0.0, "score": 0.0},
                    "mutes": {"vocals": False, "midi": True, "score": True},
                    "format": "mp3",
                },
            )

        assert response.status_code == 200
        cmd = mock_run.call_args[0][0]
        assert str(midi_path) not in cmd
        assert str(score_path) not in cmd
        assert str(vocals_path) in cmd

    def test_safe_storage_path_blocks_dotdot(self):
        """Guard de path deve rejeitar segmentos .. e separadores."""
        import tempfile
        from pathlib import Path
        from fastapi import HTTPException
        from application.routes.export import _safe_storage_path

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "exports" / "proj").mkdir(parents=True)

            ok = _safe_storage_path(base, "exports", "proj", "mix.mp3")
            assert ok.name == "mix.mp3"

            for parts in [
                ("exports", "proj", "../../secret.txt"),
                ("exports", "..", "secret.txt"),
                ("exports", "proj", "foo/bar"),
            ]:
                try:
                    _safe_storage_path(base, *parts)
                    assert False, f"should reject {parts}"
                except HTTPException as exc:
                    assert exc.status_code == 400


class TestLyricsEndpoint:
    """Testes para /api/lyrics — não deve 500 se o diretório de stems sumiu."""

    def test_lyrics_missing_stems_dir_returns_empty(self, client: TestClient, db_session):
        import uuid
        from domain.models.project import Project, ProjectStatus

        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            original_filename="song.mp3",
            original_file_path="/tmp/song.mp3",
            file_size_mb=1,
            duration_seconds=10,
            status=ProjectStatus.READY,
        )
        db_session.add(project)
        db_session.commit()

        response = client.get(f"/api/lyrics/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["lyrics"] == []


class TestCORS:
    """Testes para configuração de CORS."""
    
    def test_cors_headers_present(self, client: TestClient):
        """Headers CORS devem estar presentes nas respostas."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Deve ter headers CORS
        assert response.status_code == 200
    
    def test_cors_allowed_origin(self, client: TestClient):
        """Origem permitida deve receber resposta sem erros."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200


class TestAPIDocumentation:
    """Testes para documentação da API."""
    
    def test_docs_endpoint_accessible(self, client: TestClient):
        """Endpoint /docs deve estar acessível."""
        response = client.get("/docs")
        
        assert response.status_code == 200
    
    def test_openapi_schema_accessible(self, client: TestClient):
        """Schema OpenAPI deve estar acessível."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "IsoMix Studio API"
        assert "paths" in data
