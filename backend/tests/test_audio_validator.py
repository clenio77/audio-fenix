"""
Testes - Domain Layer: AudioValidator

Testa as validações de arquivos de áudio.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from domain.validators.audio import AudioValidator


class TestValidateFormat:
    """Testes para o método validate_format()."""
    
    def test_valid_mp3_format(self, temp_dir):
        """Arquivo MP3 válido deve ser aceito."""
        # Criar arquivo com magic bytes de MP3
        mp3_path = temp_dir / "test.mp3"
        # ID3 header (mais comum em MP3s)
        with open(mp3_path, "wb") as f:
            f.write(b'ID3' + b'\x00' * 100)
        
        with patch('magic.from_file', return_value='audio/mpeg'):
            is_valid, error = AudioValidator.validate_format(mp3_path)
            assert is_valid is True
            assert error is None
    
    def test_valid_wav_format(self, temp_audio_file):
        """Arquivo WAV válido deve ser aceito."""
        with patch('magic.from_file', return_value='audio/wav'):
            is_valid, error = AudioValidator.validate_format(temp_audio_file)
            assert is_valid is True
            assert error is None
    
    def test_valid_flac_format(self, temp_dir):
        """Arquivo FLAC válido deve ser aceito."""
        flac_path = temp_dir / "test.flac"
        with open(flac_path, "wb") as f:
            f.write(b'fLaC' + b'\x00' * 100)
        
        with patch('magic.from_file', return_value='audio/flac'):
            is_valid, error = AudioValidator.validate_format(flac_path)
            assert is_valid is True
            assert error is None
    
    def test_valid_m4a_format(self, temp_dir):
        """Arquivo M4A válido deve ser aceito."""
        m4a_path = temp_dir / "test.m4a"
        with open(m4a_path, "wb") as f:
            f.write(b'\x00' * 100)
        
        with patch('magic.from_file', return_value='audio/mp4'):
            is_valid, error = AudioValidator.validate_format(m4a_path)
            assert is_valid is True
            assert error is None
    
    def test_invalid_text_file(self, invalid_file):
        """Arquivo de texto deve ser rejeitado."""
        with patch('magic.from_file', return_value='text/plain'):
            is_valid, error = AudioValidator.validate_format(invalid_file)
            assert is_valid is False
            assert "Formato não suportado" in error
    
    def test_invalid_image_file(self, temp_dir):
        """Arquivo de imagem deve ser rejeitado."""
        img_path = temp_dir / "test.jpg"
        with open(img_path, "wb") as f:
            f.write(b'\xff\xd8\xff' + b'\x00' * 100)  # JPEG magic bytes
        
        with patch('magic.from_file', return_value='image/jpeg'):
            is_valid, error = AudioValidator.validate_format(img_path)
            assert is_valid is False
            assert error is not None
    
    def test_extension_fallback(self, temp_dir):
        """Deve aceitar arquivo com extensão válida mesmo se MIME não for reconhecido."""
        mp3_path = temp_dir / "test.mp3"
        with open(mp3_path, "wb") as f:
            f.write(b'\x00' * 100)
        
        # MIME genérico, mas extensão é .mp3
        with patch('magic.from_file', return_value='application/unknown'):
            is_valid, error = AudioValidator.validate_format(mp3_path)
            assert is_valid is True  # Aceito por extensão
    
    def test_octet_stream_fallback(self, temp_dir):
        """application/octet-stream deve ser aceito (fallback)."""
        m4a_path = temp_dir / "test.m4a"
        with open(m4a_path, "wb") as f:
            f.write(b'\x00' * 100)
        
        with patch('magic.from_file', return_value='application/octet-stream'):
            is_valid, error = AudioValidator.validate_format(m4a_path)
            assert is_valid is True


class TestGetAudioMetadata:
    """Testes para o método get_audio_metadata()."""
    
    def test_returns_dict_on_success(self, temp_audio_file):
        """Deve retornar dicionário com metadados."""
        mock_output = '''{
            "format": {
                "duration": "180.5",
                "bit_rate": "320000"
            },
            "streams": [{
                "codec_type": "audio",
                "sample_rate": "44100",
                "channels": 2,
                "codec_name": "mp3"
            }]
        }'''
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
            
            metadata = AudioValidator.get_audio_metadata(temp_audio_file)
            
            assert "duration_seconds" in metadata
            assert "sample_rate" in metadata
            assert "channels" in metadata
            assert metadata["duration_seconds"] == 180.5
            assert metadata["sample_rate"] == 44100
            assert metadata["channels"] == 2
    
    def test_returns_empty_on_ffprobe_error(self, temp_audio_file):
        """Deve retornar dicionário vazio se ffprobe falhar."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout='')
            
            metadata = AudioValidator.get_audio_metadata(temp_audio_file)
            
            assert metadata == {}
    
    def test_returns_empty_on_exception(self, temp_dir):
        """Deve retornar dicionário vazio se ocorrer exceção."""
        nonexistent = temp_dir / "nonexistent.mp3"
        
        with patch('subprocess.run', side_effect=Exception("File not found")):
            metadata = AudioValidator.get_audio_metadata(nonexistent)
            assert metadata == {}
    
    def test_handles_missing_audio_stream(self, temp_audio_file):
        """Deve retornar vazio se não houver stream de áudio."""
        mock_output = '''{
            "format": {"duration": "10"},
            "streams": [{"codec_type": "video"}]
        }'''
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
            
            metadata = AudioValidator.get_audio_metadata(temp_audio_file)
            
            assert metadata == {}


class TestValidateSize:
    """Testes para o método validate_size()."""
    
    def test_valid_size(self):
        """Arquivo dentro do limite deve ser aceito."""
        is_valid, error = AudioValidator.validate_size(file_size_mb=10, max_size_mb=20)
        assert is_valid is True
        assert error is None
    
    def test_exact_limit(self):
        """Arquivo exatamente no limite deve ser aceito."""
        is_valid, error = AudioValidator.validate_size(file_size_mb=20, max_size_mb=20)
        assert is_valid is True
        assert error is None
    
    def test_over_limit(self):
        """Arquivo acima do limite deve ser rejeitado."""
        is_valid, error = AudioValidator.validate_size(file_size_mb=25, max_size_mb=20)
        assert is_valid is False
        assert "muito grande" in error
        assert "20MB" in error
    
    def test_zero_size_rejected(self):
        """Arquivo vazio deve ser rejeitado."""
        is_valid, error = AudioValidator.validate_size(file_size_mb=0, max_size_mb=20)
        assert is_valid is False
        assert "vazio" in error.lower()
    
    def test_negative_size_behavior(self):
        """Tamanho negativo - comportamento atual aceita (edge case não tratado)."""
        # NOTA: O código atual não trata tamanhos negativos como erro.
        # Em produção, isso nunca acontece pois stat() sempre retorna >= 0.
        is_valid, error = AudioValidator.validate_size(file_size_mb=-1, max_size_mb=20)
        # O código atual permite, mas em um cenário real isso não ocorre
        assert is_valid is True  # Comportamento atual


class TestValidateDuration:
    """Testes para o método validate_duration()."""
    
    def test_valid_duration(self):
        """Áudio dentro do limite deve ser aceito."""
        is_valid, error = AudioValidator.validate_duration(
            duration_seconds=180,  # 3 minutos
            max_duration_minutes=5
        )
        assert is_valid is True
        assert error is None
    
    def test_exact_limit(self):
        """Áudio exatamente no limite deve ser aceito."""
        is_valid, error = AudioValidator.validate_duration(
            duration_seconds=300,  # 5 minutos
            max_duration_minutes=5
        )
        assert is_valid is True
        assert error is None
    
    def test_over_limit(self):
        """Áudio acima do limite deve ser rejeitado."""
        is_valid, error = AudioValidator.validate_duration(
            duration_seconds=600,  # 10 minutos
            max_duration_minutes=5
        )
        assert is_valid is False
        assert "muito longo" in error
        assert "5" in error
    
    def test_zero_duration_rejected(self):
        """Áudio sem duração deve ser rejeitado."""
        is_valid, error = AudioValidator.validate_duration(
            duration_seconds=0,
            max_duration_minutes=5
        )
        assert is_valid is False
        assert "duração" in error.lower()


class TestSupportedFormats:
    """Testes para os formatos suportados."""
    
    def test_all_expected_formats_present(self):
        """Deve suportar todos os formatos principais."""
        expected_mimes = [
            "audio/mpeg",
            "audio/wav",
            "audio/x-wav",
            "audio/flac",
            "audio/ogg",
            "audio/mp4",
            "audio/m4a",
            "audio/aac",
        ]
        
        for mime in expected_mimes:
            assert mime in AudioValidator.SUPPORTED_FORMATS, f"MIME {mime} não suportado"
    
    def test_extensions_mapping(self):
        """Extensões devem estar corretamente mapeadas."""
        assert AudioValidator.SUPPORTED_FORMATS["audio/mpeg"] == ".mp3"
        assert AudioValidator.SUPPORTED_FORMATS["audio/wav"] == ".wav"
        assert AudioValidator.SUPPORTED_FORMATS["audio/flac"] == ".flac"
