"""
Audio Validator - Domain Layer

Validações de arquivos de áudio.
"""
import magic
from pathlib import Path
from typing import Tuple, Optional
import subprocess
import json


class AudioValidator:
    """Validador de arquivos de áudio"""
    
    SUPPORTED_FORMATS = {
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/flac": ".flac",
        "audio/ogg": ".ogg",
        "audio/mp4": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/m4a": ".m4a",
        "audio/aac": ".aac",
        "audio/x-aac": ".aac",
        "application/octet-stream": ".m4a",  # Fallback genérico
    }
    
    @staticmethod
    def validate_format(file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Valida o formato do arquivo usando magic bytes (não apenas extensão).
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Verificar MIME type real
            mime = magic.from_file(str(file_path), mime=True)
            
            # Log para debug
            print(f"🔍 DEBUG: Arquivo {file_path.name} tem MIME type: {mime}")
            
            # Verificar por MIME type
            if mime in AudioValidator.SUPPORTED_FORMATS:
                print(f"✅ Aceito por MIME type: {mime}")
                return True, None
            
            # Fallback: verificar por extensão
            extension = file_path.suffix.lower()
            supported_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
            
            if extension in supported_extensions:
                print(f"✅ Aceito por extensão: {extension}")
                return True, None
            
            supported = ", ".join(AudioValidator.SUPPORTED_FORMATS.values())
            print(f"❌ Rejeitado: MIME={mime}, extensão={extension}")
            return False, f"Formato não suportado. Use: {supported}"
            
        except Exception as e:
            print(f"❌ Erro ao validar: {str(e)}")
            return False, f"Erro ao validar arquivo: {str(e)}"
    
    @staticmethod
    def get_audio_metadata(file_path: Path) -> dict:
        """
        Extrai metadados do áudio usando ffprobe.
        
        Returns:
            Dicionário com duration, bitrate, sample_rate, channels
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {}
            
            data = json.loads(result.stdout)
            
            # Extrair informações do primeiro stream de áudio
            audio_stream = next(
                (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
                None
            )
            
            if not audio_stream:
                return {}
            
            format_info = data.get("format", {})
            
            return {
                "duration_seconds": float(format_info.get("duration", 0)),
                "bitrate": int(format_info.get("bit_rate", 0)),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": int(audio_stream.get("channels", 0)),
                "codec": audio_stream.get("codec_name", "unknown"),
            }
            
        except Exception:
            return {}
    
    @staticmethod
    def validate_size(file_size_mb: float, max_size_mb: float) -> Tuple[bool, Optional[str]]:
        """
        Valida o tamanho do arquivo.
        
        Returns:
            (is_valid, error_message)
        """
        if file_size_mb > max_size_mb:
            return False, f"Arquivo muito grande. Limite: {max_size_mb}MB"
        
        if file_size_mb == 0:
            return False, "Arquivo vazio"
        
        return True, None
    
    @staticmethod
    def validate_duration(duration_seconds: float, max_duration_minutes: float) -> Tuple[bool, Optional[str]]:
        """
        Valida a duração do áudio.
        
        Returns:
            (is_valid, error_message)
        """
        duration_minutes = duration_seconds / 60
        
        if duration_minutes > max_duration_minutes:
            return False, f"Áudio muito longo. Limite: {max_duration_minutes} minutos"
        
        if duration_seconds == 0:
            return False, "Áudio sem duração válida"
        
        return True, None
