/**
 * WaveformTrack Component - Frontend
 * 
 * Exibe a visualização de waveform de um stem usando Wavesurfer.js
 * Sincronizado com o player global do MixerPage.
 */
import { useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface WaveformTrackProps {
    url: string
    color: string
    height?: number
    currentTime: number
    duration: number
    isPlaying: boolean
    volume: number
    muted: boolean
}

export interface WaveformTrackRef {
    wavesurfer: WaveSurfer | null
    seek: (time: number) => void
}

const WaveformTrack = forwardRef<WaveformTrackRef, WaveformTrackProps>(({
    url,
    color,
    height = 50,
    currentTime,
    duration,
    isPlaying: _isPlaying, // Mantido na interface para uso futuro
    volume,
    muted,
}, ref) => {
    const containerRef = useRef<HTMLDivElement>(null)
    const wavesurferRef = useRef<WaveSurfer | null>(null)
    const isSeekingRef = useRef(false)

    // Inicializar Wavesurfer (apenas para visualização)
    useEffect(() => {
        if (!containerRef.current || !url) return

        // Limpar instância anterior
        if (wavesurferRef.current) {
            wavesurferRef.current.destroy()
        }

        // Criar instância apenas para visualização
        const wavesurfer = WaveSurfer.create({
            container: containerRef.current,
            waveColor: color + '60', // Semi-transparente
            progressColor: color,
            cursorColor: '#fff',
            cursorWidth: 2,
            height,
            barWidth: 2,
            barGap: 1,
            barRadius: 2,
            normalize: true,
            backend: 'WebAudio',
            interact: false, // Interação controlada pelo MixerPage
            hideScrollbar: true,
            mediaControls: false,
        })

        wavesurfer.load(url)
        wavesurferRef.current = wavesurfer

        // Desabilitar áudio do wavesurfer (usamos os <audio> elements)
        wavesurfer.setVolume(0)

        return () => {
            wavesurfer.destroy()
        }
    }, [url, color, height])

    // Sincronizar cursor com o tempo atual
    useEffect(() => {
        if (wavesurferRef.current && duration > 0 && !isSeekingRef.current) {
            const progress = currentTime / duration
            wavesurferRef.current.seekTo(Math.min(progress, 1))
        }
    }, [currentTime, duration])

    // Expor métodos via ref
    useImperativeHandle(ref, () => ({
        wavesurfer: wavesurferRef.current,
        seek: (time: number) => {
            if (wavesurferRef.current && duration > 0) {
                isSeekingRef.current = true
                wavesurferRef.current.seekTo(time / duration)
                setTimeout(() => {
                    isSeekingRef.current = false
                }, 100)
            }
        }
    }), [duration])

    return (
        <div className="relative w-full overflow-hidden rounded-lg bg-black/30">
            {/* Container do Wavesurfer */}
            <div
                ref={containerRef}
                className={`w-full transition-opacity duration-300 ${muted ? 'opacity-30' : 'opacity-100'}`}
            />

            {/* Indicador de volume */}
            <div
                className="absolute bottom-0 left-0 h-1 transition-all duration-150"
                style={{
                    width: `${volume}%`,
                    backgroundColor: color,
                    opacity: muted ? 0.3 : 0.8
                }}
            />
        </div>
    )
})

WaveformTrack.displayName = 'WaveformTrack'

export default WaveformTrack
