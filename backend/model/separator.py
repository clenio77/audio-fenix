"""
Audio Separator - Model Layer

Interface abstrata para modelos de separação de áudio.
Permite trocar entre Demucs, Spleeter ou outros modelos facilmente.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List
from enum import Enum


class StemType(str, Enum):
    """Tipos de stems gerados"""
    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    OTHER = "other"


class AudioSeparator(ABC):
    """Interface para motores de separação de áudio"""
    
    @abstractmethod
    def separate(self, input_path: Path, output_dir: Path) -> Dict[StemType, Path]:
        """
        Separa o áudio em stems.
        
        Args:
            input_path: Caminho do arquivo de áudio original
            output_dir: Diretório onde salvar os stems
            
        Returns:
            Dicionário mapeando tipo de stem para caminho do arquivo
            
        Raises:
            AudioProcessingError: Se houver erro no processamento
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Retorna o nome do modelo sendo usado"""
        pass
    
    @abstractmethod
    def validate_audio(self, input_path: Path) -> tuple[bool, str]:
        """
        Valida se o arquivo de áudio pode ser processado.
        
        Returns:
            (is_valid, error_message)
        """
        pass


class AudioProcessingError(Exception):
    """Exceção customizada para erros de processamento de áudio"""
    pass
