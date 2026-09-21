"""
Demucs Engine - Model Layer

Implementação do separador de áudio usando o modelo Demucs (Meta Research).
"""
import logging
from pathlib import Path
from typing import Dict
import subprocess
import os

from .separator import AudioSeparator, StemType, AudioProcessingError

logger = logging.getLogger(__name__)


class DemucsEngine(AudioSeparator):
    """
    Motor de separação usando Demucs.
    
    Demucs é um modelo de Deep Learning desenvolvido pela Meta Research
    que oferece alta qualidade na separação de fontes.
    """
    
    def __init__(self, model_name: str = "htdemucs"):
        """
        Inicializa o motor Demucs.
        
        Args:
            model_name: Nome do modelo Demucs a usar
                - htdemucs: Hybrid Transformer Demucs (recomendado)
                - htdemucs_ft: Fine-tuned version
                - mdx_extra: Modelo extra de alta qualidade
        """
        self.model_name = model_name
        logger.info(f"DemucsEngine inicializado com modelo: {model_name}")
    
    def separate(self, input_path: Path, output_dir: Path) -> Dict[StemType, Path]:
        """
        Separa o áudio usando Demucs.
        
        O Demucs gera 4 stems por padrão: vocals, drums, bass, other
        """
        try:
            logger.info(f"Iniciando separação de {input_path}")
            
            # Validar arquivo
            is_valid, error_msg = self.validate_audio(input_path)
            if not is_valid:
                raise AudioProcessingError(error_msg)
            
            # Criar diretório de saída
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Executar Demucs via subprocess
            cmd = [
                "demucs",
                "-n", self.model_name,
                "-o", str(output_dir),
                str(input_path)
            ]
            
            logger.info(f"Executando comando: {' '.join(cmd)}")
            print(f"🎵 Executando Demucs: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos de timeout
            )
            
            print(f"🎵 Demucs stdout: {result.stdout}")
            print(f"🎵 Demucs stderr: {result.stderr}")
            
            if result.returncode != 0:
                logger.error(f"Erro no Demucs: {result.stderr}")
                raise AudioProcessingError(f"Demucs falhou: {result.stderr}")
            
            # Mapear arquivos gerados
            # Demucs cria: output_dir/htdemucs/nome_arquivo/vocals.wav, etc.
            stem_dir = output_dir / self.model_name / input_path.stem
            
            stems = {
                StemType.VOCALS: stem_dir / "vocals.wav",
                StemType.DRUMS: stem_dir / "drums.wav",
                StemType.BASS: stem_dir / "bass.wav",
                StemType.OTHER: stem_dir / "other.wav",
            }
            
            # Verificar se todos os stems foram gerados
            for stem_type, stem_path in stems.items():
                if not stem_path.exists():
                    raise AudioProcessingError(f"Stem {stem_type} não foi gerado")
            
            logger.info(f"Separação concluída com sucesso: {len(stems)} stems gerados")
            return stems
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError("Processamento excedeu o tempo limite (10 minutos)")
        except Exception as e:
            logger.exception("Erro inesperado na separação")
            raise AudioProcessingError(f"Erro ao processar áudio: {str(e)}")
    
    def get_model_name(self) -> str:
        """Retorna o nome do modelo"""
        return f"demucs-{self.model_name}"
    
    def validate_audio(self, input_path: Path) -> tuple[bool, str]:
        """
        Valida se o arquivo pode ser processado.
        
        Verifica:
        - Arquivo existe
        - Extensão suportada
        - Tamanho não é zero
        """
        if not input_path.exists():
            return False, "Arquivo não encontrado"
        
        if input_path.stat().st_size == 0:
            return False, "Arquivo vazio"
        
        # Must stay aligned with AudioValidator / UploadPage allowlists.
        # AAC was accepted at upload then rejected here, marking every .aac
        # project FAILED after a successful upload.
        supported_extensions = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
        if input_path.suffix.lower() not in supported_extensions:
            return False, f"Formato não suportado. Use: {', '.join(sorted(supported_extensions))}"
        
        return True, ""


# Factory para criar o separador correto
def create_separator(model_type: str = "demucs") -> AudioSeparator:
    """
    Factory para criar o separador de áudio apropriado.
    
    Args:
        model_type: Tipo de modelo ("demucs" ou "spleeter")
        
    Returns:
        Instância do separador
    """
    if model_type == "demucs":
        return DemucsEngine()
    elif model_type == "spleeter":
        # TODO: Implementar SpleeterEngine
        raise NotImplementedError("Spleeter ainda não implementado")
    else:
        raise ValueError(f"Modelo desconhecido: {model_type}")
