"""
Pytest Fixtures - IsoMix Studio

Configurações e fixtures compartilhadas para os testes.
"""
import pytest
from pathlib import Path
import tempfile
import os
import sys

# Configurar variáveis de ambiente ANTES de qualquer import do app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["STORAGE_PATH"] = tempfile.mkdtemp()


# ===============================
# File Fixtures (não dependem do app)
# ===============================

@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_audio_bytes():
    """
    Retorna bytes de um arquivo WAV mínimo válido.
    Este é um arquivo WAV de 1 segundo de silêncio.
    """
    import struct
    
    sample_rate = 8000
    num_channels = 1
    bits_per_sample = 16
    num_samples = sample_rate  # 1 segundo
    
    # Calcular tamanhos
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align
    
    # Construir header WAV
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,  # Chunk size
        b'WAVE',
        b'fmt ',
        16,  # Subchunk1 size
        1,   # Audio format (PCM)
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    # Silêncio (zeros)
    audio_data = bytes(data_size)
    
    return header + audio_data


@pytest.fixture
def temp_audio_file(temp_dir, sample_audio_bytes):
    """Cria um arquivo de áudio temporário válido."""
    audio_path = temp_dir / "test_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(sample_audio_bytes)
    return audio_path


@pytest.fixture
def invalid_file(temp_dir):
    """Cria um arquivo inválido (não é áudio)."""
    invalid_path = temp_dir / "invalid.txt"
    with open(invalid_path, "w") as f:
        f.write("This is not an audio file!")
    return invalid_path


# ===============================
# Database Fixtures (lazy loaded)
# ===============================

@pytest.fixture(scope="function")
def db_engine():
    """Cria engine SQLite em memória para testes."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    
    # Import Base apenas quando necessário
    from domain.models.base import Base
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Cria uma sessão de banco de dados para testes."""
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


# ===============================
# API Client Fixtures (lazy loaded)
# ===============================

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente HTTP para testes de API."""
    from fastapi.testclient import TestClient
    
    # Importar app de forma lazy para evitar problemas de inicialização
    # Precisamos mockar a criação do engine antes de importar
    import unittest.mock as mock
    
    # Criar um mock do database que use nossa sessão de teste
    with mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
        from application.main import app
        from domain.database import get_db_session
        
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db_session] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()
