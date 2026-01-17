/**
 * Hook useWavesurfer - Frontend
 * 
 * Hook customizado para gerenciar instâncias do Wavesurfer.js
 * Fornece visualização de waveform para cada canal do mixer.
 */
import { useEffect, useRef, useCallback, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface UseWavesurferProps {
    containerRef: React.RefObject<HTMLDivElement>
    url: string
    waveColor?: string
    progressColor?: string
    height?: number
    barWidth?: number
    barGap?: number
    cursorColor?: string
    cursorWidth?: number
}

interface UseWavesurferReturn {
    wavesurfer: WaveSurfer | null
    isReady: boolean
    isPlaying: boolean
    duration: number
    currentTime: number
    play: () => void
    pause: () => void
    stop: () => void
    seek: (time: number) => void
    setVolume: (volume: number) => void
}

export const useWavesurfer = ({
    containerRef,
    url,
    waveColor = '#a855f7',
    progressColor = '#ec4899',
    height = 60,
    barWidth = 2,
    barGap = 1,
    cursorColor = '#fff',
    cursorWidth = 2,
}: UseWavesurferProps): UseWavesurferReturn => {
    const wavesurferRef = useRef<WaveSurfer | null>(null)
    const [isReady, setIsReady] = useState(false)
    const [isPlaying, setIsPlaying] = useState(false)
    const [duration, setDuration] = useState(0)
    const [currentTime, setCurrentTime] = useState(0)

    // Inicializar Wavesurfer
    useEffect(() => {
        if (!containerRef.current || !url) return

        // Limpar instância anterior
        if (wavesurferRef.current) {
            wavesurferRef.current.destroy()
        }

        // Criar nova instância
        const wavesurfer = WaveSurfer.create({
            container: containerRef.current,
            waveColor,
            progressColor,
            cursorColor,
            cursorWidth,
            height,
            barWidth,
            barGap,
            normalize: true,
            backend: 'WebAudio',
            interact: false, // Desabilitar interação direta (controlamos via MixerPage)
            hideScrollbar: true,
        })

        // Event listeners
        wavesurfer.on('ready', () => {
            setIsReady(true)
            setDuration(wavesurfer.getDuration())
        })

        wavesurfer.on('play', () => setIsPlaying(true))
        wavesurfer.on('pause', () => setIsPlaying(false))
        wavesurfer.on('finish', () => setIsPlaying(false))

        wavesurfer.on('audioprocess', () => {
            setCurrentTime(wavesurfer.getCurrentTime())
        })

        wavesurfer.on('seeking', () => {
            setCurrentTime(wavesurfer.getCurrentTime())
        })

        // Carregar áudio
        wavesurfer.load(url)
        wavesurferRef.current = wavesurfer

        return () => {
            wavesurfer.destroy()
        }
    }, [containerRef, url, waveColor, progressColor, height, barWidth, barGap, cursorColor, cursorWidth])

    // Métodos de controle
    const play = useCallback(() => {
        wavesurferRef.current?.play()
    }, [])

    const pause = useCallback(() => {
        wavesurferRef.current?.pause()
    }, [])

    const stop = useCallback(() => {
        wavesurferRef.current?.stop()
    }, [])

    const seek = useCallback((time: number) => {
        if (wavesurferRef.current && duration > 0) {
            wavesurferRef.current.seekTo(time / duration)
        }
    }, [duration])

    const setVolume = useCallback((volume: number) => {
        wavesurferRef.current?.setVolume(volume)
    }, [])

    return {
        wavesurfer: wavesurferRef.current,
        isReady,
        isPlaying,
        duration,
        currentTime,
        play,
        pause,
        stop,
        seek,
        setVolume,
    }
}

export default useWavesurfer
