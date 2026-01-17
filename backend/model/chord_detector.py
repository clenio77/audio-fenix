"""
Chord Detector - Model Layer

Detecta os acordes de uma música usando análise de chromagram.
Versão calibrada para maior precisão.
"""
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
import json

logger = logging.getLogger(__name__)


class ChordDetector:
    """
    Detecta acordes de um arquivo de áudio usando análise de chromagram.
    Calibrado para priorizar acordes mais comuns (maior/menor).
    """
    
    # Mapeamento de notas para índices de chroma
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Templates de acordes com pesos de prioridade
    # Acordes mais comuns têm peso maior para evitar falsos positivos
    CHORD_TEMPLATES = {
        # Acordes principais (peso alto)
        'maj': {'template': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], 'weight': 1.15},  # Maior
        'min': {'template': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], 'weight': 1.10},  # Menor
        
        # Acordes com 7ª (peso médio)
        '7':   {'template': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 'weight': 1.00},  # Dominante
        'm7':  {'template': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0], 'weight': 0.95},  # Menor c/ 7ª
        'maj7':{'template': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1], 'weight': 0.90},  # Maior c/ 7ª
        
        # Acordes menos comuns (peso baixo para evitar falsos positivos)
        'sus4':{'template': [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0], 'weight': 0.75},  # Suspenso 4
        'sus2':{'template': [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0], 'weight': 0.75},  # Suspenso 2
        'dim': {'template': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0], 'weight': 0.70},  # Diminuto
        'aug': {'template': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 'weight': 0.70},  # Aumentado
    }
    
    def __init__(self, hop_length: int = 512, segment_duration: float = 1.0, 
                 min_confidence: float = 0.65):
        """
        Args:
            hop_length: Hop length para análise de chromagram
            segment_duration: Duração de cada segmento em segundos (padrão 1s)
            min_confidence: Confiança mínima para aceitar um acorde (0-1)
        """
        self.hop_length = hop_length
        self.segment_duration = segment_duration
        self.min_confidence = min_confidence
    
    def _rotate_template(self, template: List[int], semitones: int) -> np.ndarray:
        """Rotaciona o template de acorde por N semitons."""
        return np.roll(template, semitones)
    
    def _match_chord(self, chroma_vector: np.ndarray) -> Tuple[str, float]:
        """
        Encontra o acorde que melhor corresponde ao vetor de chroma.
        Usa pesos para priorizar acordes mais comuns.
        
        Returns:
            Tuple[chord_name, confidence]: Nome do acorde e confiança (0-1)
        """
        best_match = "N"  # No chord
        best_score = 0.0
        
        # Normalizar o vetor de chroma
        chroma_norm = chroma_vector / (np.linalg.norm(chroma_vector) + 1e-8)
        
        for root_idx, root_note in enumerate(self.NOTES):
            for chord_type, chord_data in self.CHORD_TEMPLATES.items():
                template = chord_data['template']
                weight = chord_data['weight']
                
                # Rotacionar template para a nota raiz
                rotated = self._rotate_template(template, root_idx)
                template_norm = rotated / (np.linalg.norm(rotated) + 1e-8)
                
                # Calcular similaridade com peso
                raw_score = np.dot(chroma_norm, template_norm)
                weighted_score = raw_score * weight
                
                if weighted_score > best_score:
                    best_score = weighted_score
                    # Formatar nome do acorde
                    if chord_type == 'maj':
                        best_match = root_note
                    elif chord_type == 'min':
                        best_match = f"{root_note}m"
                    else:
                        best_match = f"{root_note}{chord_type}"
        
        return best_match, float(best_score)
    
    def detect_chords(self, audio_path: Path) -> List[Dict]:
        """
        Detecta acordes do arquivo de áudio.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Lista de dicionários com {time, chord, confidence}
        """
        try:
            import librosa
            
            logger.info(f"Detectando acordes de {audio_path}")
            print(f"🎸 Detectando acordes de {audio_path.name}...")
            
            # Carregar áudio
            y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
            duration = len(y) / sr
            
            # Calcular chromagram usando CQT (mais preciso para música)
            chroma = librosa.feature.chroma_cqt(
                y=y, 
                sr=sr, 
                hop_length=self.hop_length,
                n_chroma=12,
                bins_per_octave=36  # Mais preciso
            )
            
            # Aplicar suavização para reduzir ruído
            from scipy.ndimage import median_filter
            chroma = median_filter(chroma, size=(1, 5))
            
            # Tempo por frame
            times = librosa.frames_to_time(
                np.arange(chroma.shape[1]), 
                sr=sr, 
                hop_length=self.hop_length
            )
            
            # Segmentar e detectar acordes
            segment_frames = int(self.segment_duration * sr / self.hop_length)
            chords = []
            
            for i in range(0, chroma.shape[1], segment_frames):
                end_idx = min(i + segment_frames, chroma.shape[1])
                
                # Usar mediana ao invés de média para robustez
                segment_chroma = np.median(chroma[:, i:end_idx], axis=1)
                
                chord, confidence = self._match_chord(segment_chroma)
                
                # Só incluir se tiver confiança mínima
                if confidence > self.min_confidence:
                    chords.append({
                        "time": float(times[i]),
                        "chord": chord,
                        "confidence": round(confidence, 2),
                        "duration": self.segment_duration
                    })
            
            # Simplificar: unir acordes consecutivos iguais
            simplified_chords = []
            for chord_info in chords:
                if simplified_chords and simplified_chords[-1]["chord"] == chord_info["chord"]:
                    simplified_chords[-1]["duration"] += chord_info["duration"]
                else:
                    simplified_chords.append(chord_info.copy())
            
            # Filtrar acordes muito curtos (provavelmente ruído)
            filtered_chords = [c for c in simplified_chords if c["duration"] >= 0.5]
            
            logger.info(f"Detectados {len(filtered_chords)} acordes")
            print(f"✅ Detectados {len(filtered_chords)} acordes")
            
            return filtered_chords
            
        except Exception as e:
            logger.exception("Erro ao detectar acordes")
            print(f"❌ Erro ao detectar acordes: {str(e)}")
            return []
    
    def save_chords(self, chords: List[Dict], output_path: Path) -> str:
        """
        Salva os acordes em um arquivo JSON.
        
        Args:
            chords: Lista de acordes detectados
            output_path: Caminho para salvar o arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chords, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Acordes salvos em {output_path}")
        print(f"💾 Acordes salvos em {output_path.name}")
        
        return str(output_path)


# Instância global com configurações calibradas
chord_detector = ChordDetector(
    hop_length=512,
    segment_duration=1.0,     # 1 segundo por segmento (mais estável)
    min_confidence=0.65       # Confiança mínima 65%
)
