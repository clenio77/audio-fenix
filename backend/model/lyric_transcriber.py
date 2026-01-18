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
        Transcreve o áudio de forma generalista (auto-idioma) e com filtros anti-alucinação.
        """
        try:
            audio_path_str = str(audio_path)
            output_path = output_dir / "lyrics.json"
            logger.info(f"Iniciando transcrição generalista para {audio_path_str}")
            
            # Configuração generalista:
            # - language=None permite que o Whisper detecte o idioma sozinho
            # - No initial_prompt para evitar distrações/vieses
            # - temperature variada para sair de loops de repetição
            result = self.model.transcribe(
                audio_path_str, 
                verbose=False, 
                fp16=False,
                language=None, # Detecção automática de idioma (PT, EN, ES, etc.)
                beam_size=5,
                best_of=5,
                temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                condition_on_previous_text=False, # Essencial para evitar o "I'm going to do it" infinito
                no_speech_threshold=0.6
            )
            
            lyrics_data = []
            # Lista expandida de frases típicas de alucinação do Whisper em silêncio
            hallucination_phrases = [
                "I'm going to do it", "Thank you for watching", "Subtitles by", 
                "Obrigado por assistir", "Legendas por", "Please subscribe",
                "Watching for watching", "Thanks for watching", "Subtitles powered by"
            ]

            for segment in result['segments']:
                text = segment['text'].strip()
                
                # FILTROS DE QUALIDADE RIGOROSOS
                # Se o Whisper está muito na dúvida se é voz (no_speech_prob > 0.4), ignoramos.
                if segment.get('no_speech_prob', 0) > 0.4:
                    continue
                
                # Se a confiança no texto é baixa (avg_logprob < -1.0), ignoramos.
                if segment.get('avg_logprob', 0) < -1.0:
                    continue

                # Se o texto contém frases clássicas de erro da IA, ignoramos.
                if any(h.lower() in text.lower() for h in hallucination_phrases):
                    continue
                
                if len(text) > 1:
                    lyrics_data.append({
                        "start": segment['start'],
                        "end": segment['end'],
                        "text": text,
                    })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(lyrics_data, f, ensure_ascii=False, indent=2)
            
            detected_lang = result.get('language', 'unknown')
            logger.info(f"Transcrição finalizada. Idioma detectado: {detected_lang}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return None

# Instância singleton - 'medium' é o nível profissional para português sem exigir GPU gigante
lyric_transcriber = LyricTranscriber(model_name="medium")
