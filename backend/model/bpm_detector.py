"""
BPM Detector & Click Track Generator - Model Layer

Detecta o BPM da música e gera um click track sincronizado.
Versão calibrada para melhor sincronização.
"""
import logging
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


class BPMDetector:
    """
    Detecta o BPM (batidas por minuto) de um arquivo de áudio
    e gera um click track sincronizado usando detecção de onsets.
    """
    
    def __init__(self, click_frequency: float = 1000, click_duration: float = 0.03):
        """
        Args:
            click_frequency: Frequência do som do click em Hz (padrão: 1000Hz)
            click_duration: Duração de cada click em segundos (padrão: 30ms)
        """
        self.click_frequency = click_frequency
        self.click_duration = click_duration
    
    def detect_bpm(self, audio_path: Path) -> Tuple[float, np.ndarray]:
        """
        Detecta o BPM e os tempos dos beats no áudio.
        Usa algoritmo de beat tracking com parâmetros calibrados.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Tuple[bpm, beat_times]: BPM estimado e array com tempos dos beats
        """
        try:
            import librosa
            
            logger.info(f"Detectando BPM de {audio_path}")
            print(f"🎵 Detectando BPM de {audio_path.name}...")
            
            # Carregar áudio
            y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
            
            # Detecção de onset para melhor precisão
            onset_env = librosa.onset.onset_strength(
                y=y, 
                sr=sr,
                hop_length=512,
                aggregate=np.median  # Mais robusto a ruído
            )
            
            # Detectar tempo (BPM) e beats com parâmetros calibrados
            tempo, beat_frames = librosa.beat.beat_track(
                y=y, 
                sr=sr,
                onset_envelope=onset_env,
                hop_length=512,
                start_bpm=120,      # BPM inicial típico
                tightness=100,       # Maior precisão na sincronização
                trim=True            # Remove beats imprecisos do início/fim
            )
            
            # Converter frames para tempo em segundos
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)
            
            # Arredondar BPM para valor mais próximo
            bpm = float(round(tempo[0] if hasattr(tempo, '__iter__') else tempo))
            
            # Validar BPM (deve estar entre 60-200 para música popular)
            if bpm < 60:
                bpm = bpm * 2  # Provavelmente detectou metade do tempo
            elif bpm > 200:
                bpm = bpm / 2  # Provavelmente detectou dobro do tempo
            
            logger.info(f"BPM detectado: {bpm} ({len(beat_times)} beats)")
            print(f"✅ BPM detectado: {bpm} ({len(beat_times)} beats)")
            
            return bpm, beat_times
            
        except Exception as e:
            logger.exception("Erro ao detectar BPM")
            print(f"❌ Erro ao detectar BPM: {str(e)}")
            # Retornar BPM padrão (120) se falhar
            return 120.0, np.array([])
    
    def refine_beat_times(self, y: np.ndarray, sr: int, beat_times: np.ndarray) -> np.ndarray:
        """
        Refina os tempos dos beats usando detecção de onset local.
        Ajusta cada beat para o onset mais próximo.
        """
        import librosa
        
        # Detectar todos os onsets
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=512)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=512)
        
        if len(onset_times) == 0:
            return beat_times
        
        refined_times = []
        window = 0.05  # 50ms de janela para ajuste
        
        for beat_time in beat_times:
            # Encontrar onset mais próximo dentro da janela
            nearby = onset_times[np.abs(onset_times - beat_time) < window]
            if len(nearby) > 0:
                # Usar o onset mais próximo
                closest = nearby[np.argmin(np.abs(nearby - beat_time))]
                refined_times.append(closest)
            else:
                refined_times.append(beat_time)
        
        return np.array(refined_times)
    
    def generate_click_track(
        self, 
        audio_path: Path, 
        output_path: Path,
        bpm: Optional[float] = None,
        beat_times: Optional[np.ndarray] = None
    ) -> Tuple[str, float]:
        """
        Gera um click track sincronizado com o áudio original.
        Usa beats detectados e refinados para máxima precisão.
        
        Args:
            audio_path: Caminho do áudio original (para obter duração)
            output_path: Caminho para salvar o click track
            bpm: BPM (se já detectado)
            beat_times: Tempos dos beats (se já detectados)
            
        Returns:
            Tuple[path, bpm]: Caminho do arquivo gerado e BPM
        """
        try:
            import librosa
            
            # Carregar áudio original
            y_original, sr_original = librosa.load(str(audio_path), sr=22050, mono=True)
            duration = len(y_original) / sr_original
            
            # Detectar BPM se não fornecido
            if bpm is None or beat_times is None or len(beat_times) == 0:
                bpm, beat_times = self.detect_bpm(audio_path)
            
            # Refinar tempos dos beats
            if len(beat_times) > 0:
                beat_times = self.refine_beat_times(y_original, sr_original, beat_times)
            
            # Se não conseguiu detectar beats, gerar baseado no BPM
            if len(beat_times) == 0:
                beat_interval = 60.0 / bpm
                # Detectar primeiro onset como ponto de partida
                onset_frames = librosa.onset.onset_detect(y=y_original, sr=sr_original)
                if len(onset_frames) > 0:
                    start_time = librosa.frames_to_time(onset_frames[0], sr=sr_original)
                else:
                    start_time = 0
                beat_times = np.arange(start_time, duration, beat_interval)
            
            # Sample rate para o click track (igual ao stem do Demucs)
            sr = 44100
            
            # Criar array de silêncio com a mesma duração
            click_track = np.zeros(int(duration * sr))
            
            # Gerar forma de onda do click (mais curto e preciso)
            click_samples = int(self.click_duration * sr)
            t = np.linspace(0, self.click_duration, click_samples)
            
            # Envelope de decaimento rápido
            envelope = np.exp(-t * 50)
            
            # Click principal (downbeat) - mais grave e mais alto
            click_main = np.sin(2 * np.pi * 900 * t) * envelope * 0.9
            
            # Click secundário (upbeat) - mais agudo e mais suave
            click_sub = np.sin(2 * np.pi * 1400 * t) * envelope * 0.5
            
            # Determinar compasso (4/4 é mais comum)
            # O primeiro beat detectado é considerado o downbeat
            
            # Inserir clicks nos tempos detectados
            for i, beat_time in enumerate(beat_times):
                sample_pos = int(beat_time * sr)
                
                # Alternar entre click principal (a cada 4 beats) e secundário
                click = click_main if i % 4 == 0 else click_sub
                
                # Inserir click
                end_pos = min(sample_pos + len(click), len(click_track))
                insert_len = end_pos - sample_pos
                
                if insert_len > 0 and sample_pos >= 0:
                    click_track[sample_pos:end_pos] += click[:insert_len]
            
            # Normalizar
            max_val = np.max(np.abs(click_track))
            if max_val > 0:
                click_track = click_track / max_val * 0.8
            
            # Converter para stereo
            click_track_stereo = np.column_stack([click_track, click_track])
            
            # Salvar como WAV
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(output_path), click_track_stereo, sr)
            
            logger.info(f"Click track gerado: {output_path} (BPM: {bpm})")
            print(f"🥁 Click track gerado: {output_path.name} (BPM: {bpm}, {len(beat_times)} beats)")
            
            return str(output_path), bpm
            
        except Exception as e:
            logger.exception("Erro ao gerar click track")
            print(f"❌ Erro ao gerar click track: {str(e)}")
            raise


# Instância global para uso
bpm_detector = BPMDetector(
    click_frequency=1000,
    click_duration=0.03  # Click mais curto para melhor precisão
)
