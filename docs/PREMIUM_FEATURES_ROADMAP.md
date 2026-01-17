# 🚀 Roadmap de Funcionalidades Premium - IsoMix Studio

## Análise de Viabilidade Técnica e Impacto

### Resumo Executivo

| Funcionalidade | Complexidade | Valor Percebido | Diferencial | Prioridade | Custo Servidor |
|----------------|--------------|-----------------|-------------|------------|----------------|
| **Pitch/Speed** | 🟢 Baixa | ⭐⭐⭐⭐⭐ | Básico | P1 - Imediata | Zero (Frontend) |
| **Loops/Regions** | 🟢 Baixa | ⭐⭐⭐⭐ | Básico | P1 - Imediata | Zero (Frontend) |
| **Smart Metronome** | 🟡 Média | ⭐⭐⭐⭐⭐ | Alto | P2 - Curto prazo | Baixo |
| **Chord AI** | 🔴 Alta | ⭐⭐⭐⭐ | Alto | P3 - Médio prazo | Médio |
| **Audio-to-MIDI** | 🔴 Alta | ⭐⭐⭐⭐⭐ | Muito Alto | P3 - Premium | Médio |

---

## 1. Pitch/Speed Control (P1 - PRIORIDADE IMEDIATA)

### Por que fazer primeiro?
- ✅ **100% Frontend** - Zero custo de servidor
- ✅ **Wavesurfer.js já suporta** - Plugin nativo
- ✅ **Essencial para músicos** - Cantores precisam transpor, guitarristas precisam desacelerar
- ✅ **Implementação: ~4 horas**

### Implementação Técnica
```typescript
// Usando Tone.js para pitch shift
import * as Tone from 'tone'

const pitchShift = new Tone.PitchShift({
  pitch: 0 // -12 a +12 semitons
}).toDestination()

// Ou usando Web Audio API nativa
audioContext.playbackRate.value = 0.75 // 75% speed
```

### Interface Proposta
```
┌──────────────────────────────────────┐
│  🎵 Key: [-] C → D# [+]   ⚡ Speed: 0.75x  │
└──────────────────────────────────────┘
```

### Dependências
- `tone.js` (~100KB) ou Web Audio API nativa
- Sem backend necessário

---

## 2. Loop de Seção / Practice Mode (P1 - PRIORIDADE IMEDIATA)

### Por que fazer primeiro?
- ✅ **Plugin nativo do Wavesurfer.js** (`wavesurfer-regions`)
- ✅ **Zero custo** - Frontend puro
- ✅ **Essencial para prática** - Todo músico precisa repetir trechos
- ✅ **Implementação: ~2 horas**

### Implementação Técnica
```typescript
import WaveSurfer from 'wavesurfer.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions'

const regions = wavesurfer.registerPlugin(RegionsPlugin.create())

regions.addRegion({
  start: 10, // segundos
  end: 25,
  color: 'rgba(255, 215, 0, 0.3)', // amarelo translúcido
  drag: true,
  resize: true,
})

// Loop automático
regions.on('region-out', (region) => {
  if (loopEnabled) {
    wavesurfer.seekTo(region.start / duration)
    wavesurfer.play()
  }
})
```

### Interface Proposta
```
┌────────────────────────────────────────────────┐
│ ▶️ [====[████LOOP████]==================] 🔁   │
│      10s        25s                     │
└────────────────────────────────────────────────┘
```

### Dependências
- `wavesurfer.js/plugins/regions` (já incluso)
- Sem backend necessário

---

## 3. Smart Metronome / BPM Detection (P2 - CURTO PRAZO)

### Por que fazer depois?
- 🟡 Requer processamento backend
- 🟡 Análise do áudio original (não dos stems)
- ✅ **Diferencial competitivo alto**

### Implementação Técnica

**Backend (Python):**
```python
import librosa

def detect_bpm(audio_path: str) -> dict:
    y, sr = librosa.load(audio_path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    
    # Gerar click track
    click_times = librosa.frames_to_time(beats, sr=sr)
    click_track = librosa.clicks(times=click_times, sr=sr)
    
    return {
        "bpm": float(tempo),
        "beat_times": click_times.tolist(),
        "click_track_path": save_click_track(click_track, sr)
    }
```

**Frontend:**
- Adicionar 5º canal "METRÔNOMO" no mixer
- Volume independente
- Toggle on/off

### Dependências
- `librosa` (Python) - já comum em processamento de áudio
- Processamento no upload (uma vez por música)
- Armazenar click track como 5º stem

### Custo
- ~5-10 segundos adicionais por upload
- ~1MB extra de storage por projeto

---

## 4. Chord AI - Detecção de Acordes (P3 - MÉDIO PRAZO)

### Por que fazer depois?
- 🔴 Requer modelo de IA treinado
- 🔴 Complexidade técnica alta
- ✅ **Muito atrativo para iniciantes**

### Opções de Implementação

**Opção A: Chord Recognition Model (recomendado)**
```python
# Usando Chordino via Vamp plugins ou modelo Transformer
from chord_recognition import ChordRecognizer

recognizer = ChordRecognizer()
chords = recognizer.predict(audio_path)
# [{"time": 0.0, "chord": "Am"}, {"time": 2.5, "chord": "G"}, ...]
```

**Opção B: API Externa**
- Usar serviços como Hooktheory ou ChordAI
- Custo: $0.01-0.05 por música

### Interface Proposta
```
┌────────────────────────────────────────────────┐
│  Am         │    G        │   D7       │  Em  │
│ ▶️ [════════|═════════════|════════════|════] │
└────────────────────────────────────────────────┘
```

### Dependências
- Modelo de ML treinado ou API externa
- ~500MB de modelo (se local)
- Processamento no upload

---

## 5. Audio-to-MIDI (P3 - FEATURE PREMIUM)

### Por que fazer por último?
- 🔴 Alta complexidade técnica
- 🔴 Requer modelo de IA específico
- ✅ **Feature premium de alto valor**
- ✅ **Diferencial competitivo máximo**

### Implementação Técnica

**Usando Basic Pitch (Spotify):**
```python
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

# Converter audio para MIDI
model_output, midi_data, note_events = predict(
    audio_path,
    ICASSP_2022_MODEL_PATH,
)

# Salvar MIDI
midi_data.write("bass_line.mid")
```

### Interface Proposta
```
┌─────────────────────────────────────────┐
│  BAIXO                                  │
│  [M] [S]                                │
│  ████████████████████                   │
│  100%                                   │
│                                         │
│  [⬇️ WAV]  [⬇️ MIDI]                    │
└─────────────────────────────────────────┘
```

### Dependências
- `basic-pitch` (Spotify, open source)
- TensorFlow/PyTorch
- ~200MB de modelo

---

## 📋 Plano de Implementação

### Fase 1 - Quick Wins (1-2 dias)
1. ✅ Implementar Pitch/Speed Control (frontend)
2. ✅ Implementar Loop/Regions (frontend com Wavesurfer)

### Fase 2 - Backend Enhancement (3-5 dias)
3. 🟡 Adicionar detecção de BPM no upload
4. 🟡 Gerar click track automático
5. 🟡 Adicionar canal de metrônomo no mixer

### Fase 3 - AI Features (1-2 semanas)
6. 🔴 Integrar Chord Recognition
7. 🔴 Integrar Basic Pitch para MIDI

### Fase 4 - Premium Features
8. 🔴 Exportar stems com pitch alterado
9. 🔴 Exportar apenas região selecionada
10. 🔴 Sincronização com notação musical

---

## 💰 Modelo de Monetização Sugerido

| Plano | Features | Preço |
|-------|----------|-------|
| **Free** | Separação básica, 3 uploads/dia | R$ 0 |
| **Pro** | + Pitch/Speed, + Loops, + Metrônomo | R$ 29/mês |
| **Studio** | + Chord AI, + MIDI Export, Ilimitado | R$ 79/mês |

---

## 🛠️ Stack Técnica Recomendada

### Frontend
- **Wavesurfer.js** - Waveform, Regions, Playback
- **Tone.js** - Pitch shifting, Effects
- **React** - Já em uso

### Backend
- **librosa** - BPM detection, audio analysis
- **basic-pitch** - Audio to MIDI
- **pychord** - Chord recognition helper

### Infraestrutura
- Processamento assíncrono com **Celery** (já em uso)
- Storage de modelos em **S3** ou local

---

## ✅ Recomendação Imediata

**Implementar agora (P1):**
1. Pitch/Speed Control - 4 horas
2. Loop Regions - 2 horas

Essas features são **100% frontend**, **zero custo adicional**, e **alto valor percebido**.

Devo implementar essas duas funcionalidades agora?
