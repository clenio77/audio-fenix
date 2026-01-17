# 🎵 Implementação do Wavesurfer.js - Fase 2

## Objetivo

Adicionar visualização de waveform (forma de onda) para cada canal do mixer, permitindo que o usuário veja visualmente o áudio enquanto ele toca.

---

## 📦 Dependências

```bash
cd frontend
npm install wavesurfer.js@7.6.0
```

---

## 🎯 Funcionalidades a Implementar

### 1. Waveform por Canal

Cada canal do mixer deve exibir:
- ✅ Forma de onda do stem
- ✅ Cursor de reprodução sincronizado
- ✅ Zoom in/out
- ✅ Cores distintas por canal

### 2. Player Global

- ✅ Play/Pause sincronizado para todos os canais
- ✅ Seek (clicar na waveform para pular)
- ✅ Loop
- ✅ Indicador de tempo (atual / total)

### 3. Sincronização

- ✅ Todos os 4 stems tocam perfeitamente sincronizados
- ✅ Latência < 10ms entre canais

---

## 🔧 Implementação

### Passo 1: Criar Hook useWavesurfer

```typescript
// frontend/src/hooks/useWavesurfer.ts
import { useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface UseWavesurferProps {
  containerRef: React.RefObject<HTMLDivElement>
  url: string
  color: string
  height?: number
}

export const useWavesurfer = ({
  containerRef,
  url,
  color,
  height = 80
}: UseWavesurferProps) => {
  const wavesurferRef = useRef<WaveSurfer | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: color,
      progressColor: `${color}80`, // 50% opacity
      cursorColor: '#fff',
      height,
      normalize: true,
      backend: 'WebAudio',
    })

    wavesurfer.load(url)
    wavesurferRef.current = wavesurfer

    return () => {
      wavesurfer.destroy()
    }
  }, [containerRef, url, color, height])

  return wavesurferRef
}
```

### Passo 2: Atualizar MixerChannel

```typescript
// frontend/src/components/MixerChannel.tsx
import { useRef } from 'react'
import { useWavesurfer } from '@/hooks/useWavesurfer'

export default function MixerChannel({
  stemType,
  stemUrl, // Nova prop
  volume,
  muted,
  solo,
  color,
  onVolumeChange,
  onMuteToggle,
  onSoloToggle,
}: MixerChannelProps) {
  const waveformRef = useRef<HTMLDivElement>(null)
  
  const wavesurfer = useWavesurfer({
    containerRef: waveformRef,
    url: stemUrl,
    color: color.replace('text-', '#'), // Converter classe CSS para hex
    height: 80,
  })

  // ... resto do componente

  return (
    <div className="mixer-channel">
      {/* ... controles existentes ... */}

      {/* Waveform */}
      <div ref={waveformRef} className="waveform-container" />
    </div>
  )
}
```

### Passo 3: Criar Player Global

```typescript
// frontend/src/components/GlobalPlayer.tsx
import { useState, useEffect } from 'react'
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react'

interface GlobalPlayerProps {
  wavesurfers: React.RefObject<WaveSurfer>[]
}

export default function GlobalPlayer({ wavesurfers }: GlobalPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  const handlePlayPause = () => {
    wavesurfers.forEach(ws => {
      if (ws.current) {
        if (isPlaying) {
          ws.current.pause()
        } else {
          ws.current.play()
        }
      }
    })
    setIsPlaying(!isPlaying)
  }

  const handleSeek = (time: number) => {
    wavesurfers.forEach(ws => {
      if (ws.current) {
        ws.current.seekTo(time / duration)
      }
    })
  }

  useEffect(() => {
    // Sincronizar tempo
    const interval = setInterval(() => {
      if (wavesurfers[0]?.current) {
        setCurrentTime(wavesurfers[0].current.getCurrentTime())
        setDuration(wavesurfers[0].current.getDuration())
      }
    }, 100)

    return () => clearInterval(interval)
  }, [wavesurfers])

  return (
    <div className="global-player">
      <button onClick={handlePlayPause}>
        {isPlaying ? <Pause /> : <Play />}
      </button>
      
      <div className="time-display">
        {formatTime(currentTime)} / {formatTime(duration)}
      </div>

      <input
        type="range"
        min={0}
        max={duration}
        value={currentTime}
        onChange={(e) => handleSeek(Number(e.target.value))}
      />
    </div>
  )
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
```

### Passo 4: Integrar no MixerPage

```typescript
// frontend/src/pages/MixerPage.tsx
import { useRef } from 'react'
import GlobalPlayer from '@/components/GlobalPlayer'

export default function MixerPage({ projectId, onBack }: MixerPageProps) {
  // ... código existente ...

  const wavesurferRefs = useRef<React.RefObject<WaveSurfer>[]>([])

  return (
    <div>
      {/* Player Global */}
      <GlobalPlayer wavesurfers={wavesurferRefs.current} />

      {/* Mixer Channels */}
      <div className="grid grid-cols-4 gap-4">
        {project.stems?.map((stem, index) => (
          <MixerChannel
            key={stem.type}
            stemType={stem.type as StemType}
            stemUrl={apiService.getDownloadUrl(stem.url)}
            wavesurferRef={wavesurferRefs.current[index]}
            // ... outras props ...
          />
        ))}
      </div>
    </div>
  )
}
```

---

## 🎨 Estilos

```css
/* frontend/src/index.css */

.global-player {
  @apply flex items-center gap-4 p-4 bg-mixer-panel rounded-lg mb-6;
}

.global-player button {
  @apply w-12 h-12 rounded-full bg-mixer-accent text-black;
  @apply hover:scale-105 transition-transform;
}

.time-display {
  @apply font-mono text-sm text-gray-400;
}

.waveform-container {
  @apply w-full h-20 bg-black/50 rounded overflow-hidden;
}

.waveform-container wave {
  @apply cursor-pointer;
}
```

---

## 🧪 Testes

### Teste Manual

1. Carregar projeto com stems
2. Verificar se waveforms aparecem
3. Clicar em Play
4. Verificar se:
   - ✅ Todos os stems tocam juntos
   - ✅ Cursores se movem sincronizados
   - ✅ Tempo é exibido corretamente

### Teste de Sincronização

```javascript
// Verificar latência entre canais
const times = wavesurfers.map(ws => ws.current?.getCurrentTime())
const maxDiff = Math.max(...times) - Math.min(...times)
console.log('Latência:', maxDiff * 1000, 'ms') // Deve ser < 10ms
```

---

## 📚 Referências

- [Wavesurfer.js Docs](https://wavesurfer-js.org/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

## ✅ Checklist de Implementação

- [ ] Instalar wavesurfer.js
- [ ] Criar hook useWavesurfer
- [ ] Atualizar MixerChannel com waveform
- [ ] Criar componente GlobalPlayer
- [ ] Integrar no MixerPage
- [ ] Adicionar estilos
- [ ] Testar sincronização
- [ ] Testar play/pause
- [ ] Testar seek
- [ ] Documentar uso
