"""
Lyric Transcriber Service
Transcreve vozes em texto (letras) com timestamps usando OpenAI Whisper.
"""
import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any

import whisper

logger = logging.getLogger(__name__)

class LyricTranscriber:
    def __init__(self, model_name: str = "base"):
        """
        Modelos disponíveis: tiny, base, small, medium, large
        'base' é um bom compromisso entre velocidade e precisão para CPU.
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Carregando modelo Whisper: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def transcribe(self, audio_path: Path, output_dir: Path) -> Optional[str]:
        """
        Transcreve o áudio e salva em JSON com timestamps.
        
        Args:
            audio_path: Caminho do arquivo de áudio (preferencialmente o stem 'vocals')
            output_dir: Diretório onde o JSON será salvo
            
        Returns:
            Caminho do arquivo JSON gerado
        """
        try:
            audio_path_str = str(audio_path)
            output_path = output_dir / "lyrics.json"

            logger.info(f"Iniciando transcrição de letras para {audio_path_str}")
            
            # Executar transcrição
            # fp16=False é essencial para CPU
            result = self.model.transcribe(audio_path_str, verbose=False, fp16=False)
            
            # Estruturar os dados
            lyrics_data = []
            for segment in result['segments']:
                lyrics_data.append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "text": segment['text'].strip(),
                })
            
            # Salvar JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(lyrics_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Transcrição concluída: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Erro crítico na transcrição de letras: {e}")
            return None

# Instância singleton
lyric_transcriber = LyricTranscriber(model_name="base")
