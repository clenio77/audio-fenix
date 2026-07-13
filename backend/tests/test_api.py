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
                "mutes": {"vocals": False, "drums": False},
            }
        )
        
        assert response.status_code == 404

    def test_export_rejects_path_traversal_format(self, client: TestClient, db_session):
        """format com path traversal não deve escapar do diretório de exports."""
        from datetime import datetime, timedelta
        from domain.models.project import Project, ProjectStatus
        from domain.models.stem import Stem
        import uuid
        import os
        from pathlib import Path

        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            original_filename="song.wav",
            original_file_path="/tmp/song.wav",
            file_size_mb=1,
            status=ProjectStatus.READY,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(project)
        db_session.add(Stem(
            id=str(uuid.uuid4()),
            project_id=project_id,
            stem_type="vocals",
            file_path="/tmp/vocals.wav",
            file_size_mb=1,
        ))
        db_session.commit()

        storage = Path(os.environ["STORAGE_PATH"])
        outside_target = storage.parent / f"pwned-export-{project_id}"
        # Relative escape from exports/<id>/mix_<id>.<format>
        malicious_format = f"wav/../../../../{outside_target.name}"

        response = client.post(
            "/api/export",
            json={
                "project_id": project_id,
                "volumes": {"vocals": 1.0},
                "mutes": {"vocals": False},
                "format": malicious_format,
            },
        )

        # Schema allowlist must reject before ffmpeg runs
        assert response.status_code == 422
        assert not outside_target.exists()

    def test_export_rejects_unknown_format(self, client: TestClient):
        """Apenas mp3 e wav são formatos válidos."""
        response = client.post(
            "/api/export",
            json={
                "project_id": "00000000-0000-0000-0000-000000000000",
                "volumes": {"vocals": 1.0},
                "mutes": {"vocals": False},
                "format": "flac",
            },
        )
        assert response.status_code == 422

    @patch("application.routes.export.subprocess.run")
    def test_export_writes_only_under_exports(
        self,
        mock_run,
        client: TestClient,
        db_session,
        sample_audio_bytes,
    ):
        """Export legítimo deve gravar apenas em STORAGE_PATH/exports/<project_id>/."""
        from datetime import datetime, timedelta
        from domain.models.project import Project, ProjectStatus
        from domain.models.stem import Stem
        import uuid
        import os
        from pathlib import Path

        project_id = str(uuid.uuid4())
        storage = Path(os.environ["STORAGE_PATH"])
        stem_path = storage / "stems" / project_id / "vocals.wav"
        stem_path.parent.mkdir(parents=True, exist_ok=True)
        stem_path.write_bytes(sample_audio_bytes)

        project = Project(
            id=project_id,
            original_filename="song.wav",
            original_file_path=str(storage / "uploads" / "song.wav"),
            file_size_mb=1,
            status=ProjectStatus.READY,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(project)
        db_session.add(Stem(
            id=str(uuid.uuid4()),
            project_id=project_id,
            stem_type="vocals",
            file_path=str(stem_path),
            file_size_mb=1,
        ))
        db_session.commit()

        def fake_ffmpeg(cmd, **kwargs):
            out = Path(cmd[-1])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"fake-mp3")
            return MagicMock(returncode=0, stderr="")

        mock_run.side_effect = fake_ffmpeg

        response = client.post(
            "/api/export",
            json={
                "project_id": project_id,
                "volumes": {"vocals": 1.0},
                "mutes": {"vocals": False},
                "format": "mp3",
            },
        )

        assert response.status_code == 200
        expected = (storage / "exports" / project_id / f"mix_{project_id}.mp3").resolve()
        assert expected.is_file()
        assert expected.is_relative_to((storage / "exports").resolve())
        assert mock_run.called
        assert Path(mock_run.call_args[0][0][-1]).resolve() == expected


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
