"""
Music Transcriber Service
Converte áudio em MIDI e MusicXML usando Spotify's Basic Pitch e Music21.
"""
import logging
import os
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import music21

logger = logging.getLogger(__name__)

class MusicTranscriber:
    def __init__(self):
        self.model_path = ICASSP_2022_MODEL_PATH
        # Configurar music21 para não tentar abrir visualizadores externos
        music21.environment.set('graphicsMagickPath', '')
        music21.environment.set('musescoreDirectPNGPath', '')

    def transcribe(self, audio_path: Path, output_dir: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Transcreve áudio para MIDI e MusicXML.
        
        Args:
            audio_path: Caminho do arquivo de áudio (preferencialmente o stem 'piano' ou melodia)
            output_dir: Diretório onde os resultados serão salvos
            
        Returns:
            Tuple com (caminho_midi, caminho_xml)
        """
        try:
            audio_path_str = str(audio_path)
            midi_filename = audio_path.stem + "_transcription.mid"
            xml_filename = audio_path.stem + "_score.musicxml"
            
            midi_output_path = output_dir / midi_filename
            xml_output_path = output_dir / xml_filename

            logger.info(f"Iniciando transcrição de {audio_path_str}")

            # 1. Inferência com Basic Pitch (Gera MIDI)
            # model_output, midi_data, note_events
            _, midi_data, _ = predict(audio_path_str, self.model_path)
            
            # Salvar MIDI
            midi_data.write(str(midi_output_path))
            logger.info(f"MIDI gerado em: {midi_output_path}")

            # 2. Converter MIDI para MusicXML usando music21
            try:
                score = music21.converter.parse(str(midi_output_path))
                # Tentar quantizar para deixar a partitura mais legível
                score.quantize()
                
                # Salvar em MusicXML
                score.write('musicxml', fp=str(xml_output_path))
                logger.info(f"MusicXML gerado em: {xml_output_path}")
            except Exception as e:
                logger.error(f"Erro ao converter para MusicXML: {e}")
                xml_output_path = None

            return str(midi_output_path), str(xml_output_path) if xml_output_path else None

        except Exception as e:
            logger.error(f"Erro crítico na transcrição: {e}")
            return None, None

# Instância singleton
music_transcriber = MusicTranscriber()
