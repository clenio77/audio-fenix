/**
 * Hook useAudioEngine - Frontend
 * 
 * Engine de áudio avançada usando Tone.js para:
 * - Pitch shifting em tempo real
 * - Controle de velocidade sem alterar pitch
 * - Sincronização de múltiplas tracks
 */
import { useRef, useCallback, useState, useEffect } from 'react'
import * as Tone from 'tone'
import { StemType } from '@/types'

interface StemPlayer {
    player: Tone.Player
    pitchShift: Tone.PitchShift
    gain: Tone.Gain
}

interface UseAudioEngineProps {
    stems: Array<{
        type: StemType
        url: string
    }>
    onTimeUpdate?: (time: number) => void
    onDurationReady?: (duration: number) => void
}

interface UseAudioEngineReturn {
    isReady: boolean
    isPlaying: boolean
    currentTime: number
    duration: number
    pitch: number
    speed: number

    // Controles
    play: () => Promise<void>
    pause: () => void
    stop: () => void
    seek: (time: number) => void
    setPitch: (semitones: number) => void
    setSpeed: (rate: number) => void
    setVolume: (stem: StemType, volume: number) => void
    setMute: (stem: StemType, muted: boolean) => void
}

export const useAudioEngine = ({
    stems,
    onTimeUpdate,
    onDurationReady,
}: UseAudioEngineProps): UseAudioEngineReturn => {
    const playersRef = useRef<Map<StemType, StemPlayer>>(new Map())
    const [isReady, setIsReady] = useState(false)
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [duration, setDuration] = useState(0)
    const [pitch, setPitchState] = useState(0)
    const [speed, setSpeedState] = useState(1)
    const animationFrameRef = useRef<number | null>(null)
    const startTimeRef = useRef<number>(0)
    const offsetTimeRef = useRef<number>(0)

    // Inicializar players
    useEffect(() => {
        if (!stems || stems.length === 0) return

        const initPlayers = async () => {
            try {
                // Limpar players anteriores
                playersRef.current.forEach(({ player, pitchShift, gain }) => {
                    player.dispose()
                    pitchShift.dispose()
                    gain.dispose()
                })
                playersRef.current.clear()

                // Criar players para cada stem
                const loadPromises = stems.map(async (stem) => {
                    const player = new Tone.Player({
                        url: stem.url,
                        onload: () => {
                            console.log(`Loaded: ${stem.type}`)
                        },
                    })

                    // Pitch shifter (-12 a +12 semitons)
                    const pitchShift = new Tone.PitchShift({
                        pitch: 0,
                        windowSize: 0.1,
                        delayTime: 0,
                        feedback: 0,
                    })

                    // Gain node para volume
                    const gain = new Tone.Gain(1)

                    // Conectar: Player -> PitchShift -> Gain -> Output
                    player.connect(pitchShift)
                    pitchShift.connect(gain)
                    gain.toDestination()

                    playersRef.current.set(stem.type, {
                        player,
                        pitchShift,
                        gain,
                    })

                    return player.loaded
                })

                await Promise.all(loadPromises)

                // Obter duração do primeiro player
                const firstPlayer = playersRef.current.values().next().value
                if (firstPlayer) {
                    const dur = firstPlayer.player.buffer.duration
                    setDuration(dur)
                    onDurationReady?.(dur)
                }

                setIsReady(true)
                console.log('Audio engine ready with', playersRef.current.size, 'stems')
            } catch (error) {
                console.error('Error initializing audio engine:', error)
            }
        }

        initPlayers()

        return () => {
            // Cleanup
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current)
            }
            playersRef.current.forEach(({ player, pitchShift, gain }) => {
                player.dispose()
                pitchShift.dispose()
                gain.dispose()
            })
            playersRef.current.clear()
        }
    }, [stems, onDurationReady])

    // Update loop para currentTime
    const updateTime = useCallback(() => {
        if (isPlaying && Tone.Transport.state === 'started') {
            const elapsed = Tone.now() - startTimeRef.current
            const newTime = Math.min(offsetTimeRef.current + elapsed * speed, duration)
            setCurrentTime(newTime)
            onTimeUpdate?.(newTime)

            // Auto-stop ao final
            if (newTime >= duration) {
                setIsPlaying(false)
                setCurrentTime(duration)
                return
            }
        }

        if (isPlaying) {
            animationFrameRef.current = requestAnimationFrame(updateTime)
        }
    }, [isPlaying, speed, duration, onTimeUpdate])

    useEffect(() => {
        if (isPlaying) {
            animationFrameRef.current = requestAnimationFrame(updateTime)
        }
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current)
            }
        }
    }, [isPlaying, updateTime])

    // Play
    const play = useCallback(async () => {
        if (!isReady) return

        try {
            // Iniciar Tone.js context
            await Tone.start()

            const currentOffset = currentTime

            // Iniciar todos os players sincronizados
            playersRef.current.forEach(({ player }) => {
                if (player.buffer.loaded) {
                    player.playbackRate = speed
                    player.start(Tone.now(), currentOffset)
                }
            })

            startTimeRef.current = Tone.now()
            offsetTimeRef.current = currentOffset
            setIsPlaying(true)
            Tone.Transport.start()
        } catch (error) {
            console.error('Error playing:', error)
        }
    }, [isReady, currentTime, speed])

    // Pause
    const pause = useCallback(() => {
        playersRef.current.forEach(({ player }) => {
            player.stop()
        })

        // Salvar posição atual
        offsetTimeRef.current = currentTime
        setIsPlaying(false)
        Tone.Transport.pause()
    }, [currentTime])

    // Stop
    const stop = useCallback(() => {
        playersRef.current.forEach(({ player }) => {
            player.stop()
        })

        offsetTimeRef.current = 0
        startTimeRef.current = 0
        setCurrentTime(0)
        setIsPlaying(false)
        Tone.Transport.stop()
    }, [])

    // Seek
    const seek = useCallback((time: number) => {
        const wasPlaying = isPlaying

        // Parar todos os players
        playersRef.current.forEach(({ player }) => {
            player.stop()
        })

        offsetTimeRef.current = time
        setCurrentTime(time)

        // Se estava tocando, reiniciar da nova posição
        if (wasPlaying) {
            playersRef.current.forEach(({ player }) => {
                if (player.buffer.loaded) {
                    player.playbackRate = speed
                    player.start(Tone.now(), time)
                }
            })
            startTimeRef.current = Tone.now()
        }
    }, [isPlaying, speed])

    // Set Pitch (em semitons, -12 a +12)
    const setPitch = useCallback((semitones: number) => {
        const clampedPitch = Math.max(-12, Math.min(12, semitones))

        playersRef.current.forEach(({ pitchShift }) => {
            pitchShift.pitch = clampedPitch
        })

        setPitchState(clampedPitch)
        console.log(`Pitch set to: ${clampedPitch} semitones`)
    }, [])

    // Set Speed (0.5 a 1.5)
    const setSpeed = useCallback((rate: number) => {
        const clampedRate = Math.max(0.5, Math.min(1.5, rate))

        playersRef.current.forEach(({ player }) => {
            player.playbackRate = clampedRate
        })

        setSpeedState(clampedRate)
    }, [])

    // Set Volume (0-100 para uma stem específica)
    const setVolume = useCallback((stem: StemType, volume: number) => {
        const stemPlayer = playersRef.current.get(stem)
        if (stemPlayer) {
            // Converter 0-100 para 0-1
            stemPlayer.gain.gain.value = volume / 100
        }
    }, [])

    // Set Mute
    const setMute = useCallback((stem: StemType, muted: boolean) => {
        const stemPlayer = playersRef.current.get(stem)
        if (stemPlayer) {
            stemPlayer.gain.gain.value = muted ? 0 : 1
        }
    }, [])

    return {
        isReady,
        isPlaying,
        currentTime,
        duration,
        pitch,
        speed,
        play,
        pause,
        stop,
        seek,
        setPitch,
        setSpeed,
        setVolume,
        setMute,
    }
}

export default useAudioEngine
