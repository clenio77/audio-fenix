/**
 * Mixer Page - Frontend
 * 
 * Interface profissional do mixer com:
 * - Player de áudio sincronizado
 * - Pitch Shift REAL com Tone.js
 * - Speed Control
 * - Loop Regions
 * - Faders de volume
 * - Chord Display (acordes em tempo real)
 * - Waveform visualization
 */
import { useState, useEffect, useRef } from 'react'
import {
    ArrowLeft, Download, Loader2, Play, Pause, Square, RotateCcw, Headphones,
    Repeat, Guitar, Waves, Zap
} from 'lucide-react'
import { apiService } from '@/services/api'
import { ProjectStatus, StemType, type Project, type ChordInfo } from '@/types'
import WaveformTrack from '@/components/WaveformTrack'
import PitchControl from '@/components/PitchControl'
import SpeedControl from '@/components/SpeedControl'
import SheetMusicViewer from '@/components/SheetMusicViewer'

interface MixerPageProps {
    projectId: string
    onBack: () => void
}

export default function MixerPage({ projectId, onBack }: MixerPageProps) {
    const [project, setProject] = useState<Project | null>(null)
    const [loading, setLoading] = useState(true)
    const [exporting, setExporting] = useState(false)

    // Estado do player
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [duration, setDuration] = useState(0)

    // Pitch e Speed
    const [pitch, setPitch] = useState(0) // -12 a +12 semitons
    const [speed, setSpeed] = useState(1) // 0.5 a 1.5

    // Loop
    const [loopEnabled, setLoopEnabled] = useState(false)
    const [loopStart, setLoopStart] = useState(0)
    const [loopEnd, setLoopEnd] = useState(0)

    // Acordes
    const [chords, setChords] = useState<ChordInfo[]>([])
    const [currentChord, setCurrentChord] = useState<string>('')

    // Visualização
    const [showScore, setShowScore] = useState(false)

    // Refs para os elementos de áudio
    const audioRefs = useRef<Record<string, HTMLAudioElement | null>>({})
    const audioContextRef = useRef<AudioContext | null>(null)
    const gainNodesRef = useRef<Record<string, GainNode>>({})

    // Estado do mixer
    const [volumes, setVolumes] = useState<Record<StemType, number>>({
        [StemType.VOCALS]: 100,
        [StemType.DRUMS]: 100,
        [StemType.BASS]: 100,
        [StemType.OTHER]: 100,
        [StemType.CLICK]: 50,
        [StemType.MIDI]: 0,
        [StemType.SCORE]: 0,
    })

    const [mutes, setMutes] = useState<Record<StemType, boolean>>({
        [StemType.VOCALS]: false,
        [StemType.DRUMS]: false,
        [StemType.BASS]: false,
        [StemType.OTHER]: false,
        [StemType.CLICK]: true,
        [StemType.MIDI]: true,
        [StemType.SCORE]: true,
    })

    const [solos, setSolos] = useState<Record<StemType, boolean>>({
        [StemType.VOCALS]: false,
        [StemType.DRUMS]: false,
        [StemType.BASS]: false,
        [StemType.OTHER]: false,
        [StemType.CLICK]: false,
        [StemType.MIDI]: false,
        [StemType.SCORE]: false,
    })

    const hasSoloActive = Object.values(solos).some(s => s)

    // Inicializar Audio Context
    useEffect(() => {
        if (!audioContextRef.current) {
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
        }
        return () => {
            audioContextRef.current?.close()
        }
    }, [])

    // Polling para verificar status
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const data = await apiService.getProjectStatus(projectId)
                setProject(data)

                if (data.status === ProjectStatus.READY) {
                    setLoading(false)
                } else if (data.status === ProjectStatus.FAILED) {
                    setLoading(false)
                    alert('Erro no processamento: ' + data.error)
                }
            } catch (error) {
                console.error('Erro ao verificar status:', error)
            }
        }

        checkStatus()

        const interval = setInterval(() => {
            if (loading) {
                checkStatus()
            }
        }, 3000)

        return () => clearInterval(interval)
    }, [projectId, loading])

    // Buscar acordes quando o projeto estiver pronto
    useEffect(() => {
        const fetchChords = async () => {
            if (!loading && project?.status === ProjectStatus.READY) {
                try {
                    const result = await apiService.getChords(projectId)
                    setChords(result.chords || [])
                } catch (error) {
                    console.error('Erro ao buscar acordes:', error)
                }
            }
        }
        fetchChords()
    }, [projectId, loading, project?.status])

    // Atualizar acorde atual baseado no tempo
    useEffect(() => {
        if (chords.length > 0) {
            const chord = chords.find(c => currentTime >= c.time && currentTime < c.time + c.duration)
            setCurrentChord(chord?.chord || '')
        }
    }, [currentTime, chords])

    // Atualizar volumes dos áudios
    useEffect(() => {
        Object.entries(audioRefs.current).forEach(([stemType, audio]) => {
            if (audio) {
                const stem = stemType as StemType
                const isMuted = mutes[stem] || (hasSoloActive && !solos[stem])

                // Usar GainNode para volume (mais suave)
                const gainNode = gainNodesRef.current[stemType]
                if (gainNode) {
                    gainNode.gain.value = isMuted ? 0 : volumes[stem] / 100
                } else {
                    audio.volume = isMuted ? 0 : volumes[stem] / 100
                }
            }
        })
    }, [volumes, mutes, solos, hasSoloActive])

    // Atualizar playback rate (speed)
    useEffect(() => {
        Object.values(audioRefs.current).forEach(audio => {
            if (audio) {
                audio.playbackRate = speed
            }
        })
    }, [speed])

    // Atualizar tempo atual e verificar loop
    useEffect(() => {
        const updateTime = () => {
            const firstAudio = Object.values(audioRefs.current).find(a => a)
            if (firstAudio) {
                setCurrentTime(firstAudio.currentTime)
                setDuration(firstAudio.duration || 0)

                // Verificar se deve fazer loop
                if (loopEnabled && loopEnd > loopStart) {
                    if (firstAudio.currentTime >= loopEnd) {
                        Object.values(audioRefs.current).forEach(audio => {
                            if (audio) audio.currentTime = loopStart
                        })
                    }
                }
            }
        }

        const interval = setInterval(updateTime, 50)
        return () => clearInterval(interval)
    }, [loopEnabled, loopStart, loopEnd])

    // Definir loop end baseado na duração
    useEffect(() => {
        if (duration > 0 && loopEnd === 0) {
            setLoopEnd(duration)
        }
    }, [duration, loopEnd])

    const handleVolumeChange = (stem: StemType, value: number) => {
        setVolumes(prev => ({ ...prev, [stem]: value }))
    }

    const handleMuteToggle = (stem: StemType) => {
        setMutes(prev => ({ ...prev, [stem]: !prev[stem] }))
    }

    const handleSoloToggle = (stem: StemType) => {
        setSolos(prev => ({ ...prev, [stem]: !prev[stem] }))
    }

    const handlePlay = async () => {
        // Resumir AudioContext se estiver suspenso
        if (audioContextRef.current?.state === 'suspended') {
            await audioContextRef.current.resume()
        }

        Object.values(audioRefs.current).forEach(audio => {
            if (audio) audio.play()
        })
        setIsPlaying(true)
    }

    const handlePause = () => {
        Object.values(audioRefs.current).forEach(audio => {
            if (audio) audio.pause()
        })
        setIsPlaying(false)
    }

    const handleStop = () => {
        Object.values(audioRefs.current).forEach(audio => {
            if (audio) {
                audio.pause()
                audio.currentTime = loopEnabled ? loopStart : 0
            }
        })
        setIsPlaying(false)
        setCurrentTime(loopEnabled ? loopStart : 0)
    }

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        const time = parseFloat(e.target.value)
        Object.values(audioRefs.current).forEach(audio => {
            if (audio) audio.currentTime = time
        })
        setCurrentTime(time)
    }

    const handleSpeedChange = (delta: number) => {
        const newSpeed = Math.max(0.5, Math.min(1.5, +(speed + delta).toFixed(2)))
        setSpeed(newSpeed)
    }

    const handleLoopStartChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseFloat(e.target.value)
        if (value < loopEnd) {
            setLoopStart(value)
        }
    }

    const handleLoopEndChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseFloat(e.target.value)
        if (value > loopStart) {
            setLoopEnd(value)
        }
    }

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const handleExport = async () => {
        setExporting(true)
        try {
            const normalizedVolumes = Object.entries(volumes).reduce((acc, [key, value]) => {
                acc[key as StemType] = value / 100
                return acc
            }, {} as Record<StemType, number>)

            const response = await apiService.exportMix({
                project_id: projectId,
                volumes: normalizedVolumes,
                mutes,
                format: 'mp3',
            })

            window.open(apiService.getDownloadUrl(response.download_url), '_blank')
        } catch (error) {
            alert('Erro ao exportar mix')
            console.error(error)
        } finally {
            setExporting(false)
        }
    }

    if (loading || !project) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full blur-xl opacity-50 animate-pulse" />
                    <Loader2 className="relative w-20 h-20 text-pink-400 animate-spin mb-4" />
                </div>
                <h2 className="text-3xl font-bold mb-3 text-white">Processando áudio...</h2>
                <p className="text-gray-400 mb-6">{project?.message || 'Aguarde enquanto nossa IA separa as faixas'}</p>
                {project && (
                    <div className="mt-4 w-80">
                        <div className="h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
                            <div className="h-full bg-gradient-to-r from-pink-500 to-purple-600 transition-all duration-500" style={{ width: `${project.progress}%` }} />
                        </div>
                        <p className="text-center mt-3 text-lg font-mono text-pink-400">{project.progress}%</p>
                    </div>
                )}
            </div>
        )
    }

    const stemConfig: Record<string, any> = {
        [StemType.VOCALS]: { icon: '🎤', label: 'VOCAL', gradient: 'from-pink-600/30 to-purple-600/30', border: 'border-pink-500/30', faderColor: 'from-pink-500 to-pink-400', buttonColor: 'bg-pink-500', textColor: 'text-pink-400', hexColor: '#ec4899' },
        [StemType.DRUMS]: { icon: '🥁', label: 'BATERIA', gradient: 'from-orange-600/30 to-amber-600/30', border: 'border-orange-500/30', faderColor: 'from-orange-500 to-yellow-400', buttonColor: 'bg-orange-500', textColor: 'text-orange-400', hexColor: '#f97316' },
        [StemType.BASS]: { icon: '🎸', label: 'BAIXO', gradient: 'from-green-600/30 to-emerald-600/30', border: 'border-green-500/30', faderColor: 'from-green-500 to-emerald-400', buttonColor: 'bg-green-500', textColor: 'text-green-400', hexColor: '#22c55e' },
        [StemType.OTHER]: { icon: '🎹', label: 'OUTROS', gradient: 'from-violet-600/30 to-purple-600/30', border: 'border-violet-500/30', faderColor: 'from-violet-500 to-purple-400', buttonColor: 'bg-violet-500', textColor: 'text-violet-400', hexColor: '#8b5cf6' },
        [StemType.CLICK]: { icon: '🎵', label: 'METRÔNOMO', gradient: 'from-cyan-600/30 to-blue-600/30', border: 'border-cyan-500/30', faderColor: 'from-cyan-500 to-blue-400', buttonColor: 'bg-cyan-500', textColor: 'text-cyan-400', hexColor: '#06b6d4' },
    }

    const stemOrder = [StemType.VOCALS, StemType.DRUMS, StemType.BASS, StemType.OTHER, StemType.CLICK]

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black relative overflow-hidden">
            {/* Waveform Background */}
            <div className="absolute inset-0 opacity-5 pointer-events-none flex items-end justify-center pb-20">
                <svg viewBox="0 0 1200 200" className="w-full h-32">
                    {[...Array(60)].map((_, i) => (
                        <rect key={i} x={i * 20} y={100 - Math.sin(i * 0.3) * 50 - Math.random() * 30}
                            width="8" height={Math.sin(i * 0.3) * 100 + Math.random() * 60 + 20} fill="url(#waveGradient)" rx="4" />
                    ))}
                    <defs>
                        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#a855f7" />
                            <stop offset="100%" stopColor="#ec4899" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>

            {/* Elementos de áudio ocultos - apenas tipos de áudio */}
            {project.stems?.filter(stem => [StemType.VOCALS, StemType.DRUMS, StemType.BASS, StemType.OTHER, StemType.CLICK].includes(stem.type as StemType)).map(stem => (
                <audio
                    key={stem.type}
                    ref={el => { audioRefs.current[stem.type] = el }}
                    src={apiService.getDownloadUrl(stem.url)}
                    preload="auto"
                />
            ))}

            {/* Header */}
            <div className="relative z-10 flex items-center justify-between px-8 py-6">
                <button onClick={onBack} className="flex items-center gap-2 px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all">
                    <ArrowLeft className="w-5 h-5" />
                    <span>Voltar</span>
                </button>

                <div className="flex items-center gap-3">
                    {project.stems?.some(s => s.type === StemType.SCORE) && (
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setShowScore(!showScore)}
                                className={`flex items-center gap-2 px-4 py-3 font-semibold rounded-xl transition-all border ${showScore ? 'bg-purple-600 text-white border-purple-400 shadow-lg shadow-purple-500/20' : 'bg-white/5 text-gray-300 border-white/10 hover:bg-white/10'}`}
                            >
                                <Zap className={`w-5 h-5 ${showScore ? 'text-white' : 'text-purple-400'}`} />
                                <span>{showScore ? 'Ocultar Partitura' : 'Ver Partitura'}</span>
                            </button>

                            <button
                                onClick={() => {
                                    const score = project.stems?.find(s => s.type === StemType.SCORE);
                                    if (score) window.open(apiService.getDownloadUrl(score.url), '_blank');
                                }}
                                className="flex items-center justify-center p-3 bg-white/5 text-gray-300 rounded-xl hover:bg-white/10 transition-all border border-white/10"
                                title="Baixar MusicXML"
                            >
                                <Download className="w-5 h-5 text-purple-400" />
                            </button>
                        </div>
                    )}

                    {project.stems?.some(s => s.type === StemType.MIDI) && (
                        <button
                            onClick={() => {
                                const midi = project.stems?.find(s => s.type === StemType.MIDI);
                                if (midi) window.open(apiService.getDownloadUrl(midi.url), '_blank');
                            }}
                            className="flex items-center gap-2 px-4 py-3 bg-white/5 text-gray-300 font-semibold rounded-xl hover:bg-white/10 transition-all border border-white/10"
                        >
                            <Download className="w-5 h-5 text-blue-400" />
                            <span>Baixar MIDI</span>
                        </button>
                    )}

                    <button onClick={handleExport} disabled={exporting}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-xl hover:from-pink-400 hover:to-purple-500 transition-all shadow-lg shadow-purple-500/25 disabled:opacity-50">
                        <Download className="w-5 h-5" />
                        {exporting ? 'Exportando...' : 'Exportar Mix'}
                    </button>
                </div>
            </div>

            {/* Chord Display */}
            {currentChord && (
                <div className="relative z-10 px-8 mb-4">
                    <div className="bg-gradient-to-r from-amber-600/20 via-orange-600/20 to-amber-600/20 backdrop-blur-xl rounded-2xl p-6 border border-amber-500/30">
                        <div className="flex items-center justify-center gap-4">
                            <Guitar className="w-8 h-8 text-amber-400" />
                            <div className="text-center">
                                <span className="text-sm text-amber-300/80">ACORDE ATUAL</span>
                                <div className="text-5xl font-bold text-amber-400 font-mono tracking-wider animate-pulse">
                                    {currentChord}
                                </div>
                            </div>
                            <Guitar className="w-8 h-8 text-amber-400" />
                        </div>
                    </div>
                </div>
            )}

            {/* Sheet Music Viewer Section */}
            {showScore && project.stems?.some(s => s.type === StemType.SCORE) && (
                <div className="relative z-10 px-8 mb-4 animate-in fade-in slide-in-from-top-4 duration-500">
                    <SheetMusicViewer
                        xmlUrl={apiService.getDownloadUrl(project.stems.find(s => s.type === StemType.SCORE)!.url)}
                        currentTime={currentTime}
                        isPlaying={isPlaying}
                    />
                </div>
            )}

            {/* Pitch & Speed Controls */}
            <div className="relative z-10 px-8 mb-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Pitch Control - Em desenvolvimento */}
                    <div className="relative">
                        <PitchControl
                            pitch={pitch}
                            onChange={(newPitch) => {
                                setPitch(newPitch)
                                // TODO: Implementar pitch shift real com Tone.Player
                            }}
                            disabled={true}
                        />
                        <div className="absolute inset-0 bg-black/50 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                            <span className="text-xs text-gray-400 bg-gray-800/80 px-3 py-1 rounded-full">
                                🔧 Em desenvolvimento
                            </span>
                        </div>
                    </div>

                    {/* Speed Control - Funcional */}
                    <SpeedControl
                        speed={speed}
                        onChange={(newSpeed) => {
                            setSpeed(newSpeed)
                            handleSpeedChange(newSpeed - speed)
                        }}
                    />
                </div>

                {/* Info */}
                <div className="mt-3 text-center">
                    <span className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-xs text-blue-400">
                        <Zap className="w-3 h-3" />
                        Speed funcional • Pitch shift em desenvolvimento
                    </span>
                </div>
            </div>

            {/* Player Transport com Loop */}
            <div className="relative z-10 px-8 mb-4">
                <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-4 border border-white/10">
                    <div className="flex items-center gap-4">
                        {/* Controles de transporte */}
                        <div className="flex items-center gap-2">
                            <button onClick={() => { Object.values(audioRefs.current).forEach(a => { if (a) a.currentTime = loopEnabled ? loopStart : 0 }); setCurrentTime(loopEnabled ? loopStart : 0) }}
                                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all">
                                <RotateCcw className="w-4 h-4 text-gray-400" />
                            </button>

                            <button onClick={isPlaying ? handlePause : handlePlay}
                                className="p-3 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 transition-all">
                                {isPlaying ? <Pause className="w-5 h-5 text-white" /> : <Play className="w-5 h-5 text-white ml-0.5" />}
                            </button>

                            <button onClick={handleStop} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all">
                                <Square className="w-4 h-4 text-gray-400" />
                            </button>
                        </div>

                        <span className="font-mono text-sm text-gray-400 w-12">{formatTime(currentTime)}</span>

                        {/* Barra de progresso com região de loop */}
                        <div className="flex-1 relative h-8">
                            {/* Região de loop */}
                            {loopEnabled && duration > 0 && (
                                <div
                                    className="absolute top-0 h-full bg-amber-500/20 border-l-2 border-r-2 border-amber-400 rounded"
                                    style={{
                                        left: `${(loopStart / duration) * 100}%`,
                                        width: `${((loopEnd - loopStart) / duration) * 100}%`,
                                    }}
                                />
                            )}

                            <input
                                type="range"
                                min={0}
                                max={duration || 0}
                                value={currentTime}
                                onChange={handleSeek}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                            />

                            {/* Visual da barra */}
                            <div className="absolute top-1/2 -translate-y-1/2 w-full h-2 bg-gray-700 rounded-full">
                                <div
                                    className="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full"
                                    style={{ width: `${(currentTime / (duration || 1)) * 100}%` }}
                                />
                            </div>

                            {/* Cursor */}
                            <div
                                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg transform -translate-x-1/2"
                                style={{ left: `${(currentTime / (duration || 1)) * 100}%` }}
                            />
                        </div>

                        <span className="font-mono text-sm text-gray-500 w-12">{formatTime(duration)}</span>

                        {/* Loop Toggle */}
                        <button
                            onClick={() => setLoopEnabled(!loopEnabled)}
                            className={`p-2 rounded-lg transition-all ${loopEnabled ? 'bg-amber-500 text-black' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                            title="Loop"
                        >
                            <Repeat className="w-5 h-5" />
                        </button>

                        <Headphones className={`w-5 h-5 ${isPlaying ? 'text-pink-400 animate-pulse' : 'text-gray-500'}`} />
                    </div>

                    {/* Controles de Loop (expandido) */}
                    {loopEnabled && (
                        <div className="mt-4 pt-4 border-t border-white/10">
                            <div className="flex items-center justify-center gap-6">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-gray-400">Loop Start:</span>
                                    <input
                                        type="range"
                                        min={0}
                                        max={duration}
                                        step={0.1}
                                        value={loopStart}
                                        onChange={handleLoopStartChange}
                                        className="w-32 h-2 bg-gray-700 rounded-full appearance-none cursor-pointer
                      [&::-webkit-slider-thumb]:appearance-none
                      [&::-webkit-slider-thumb]:w-3
                      [&::-webkit-slider-thumb]:h-3
                      [&::-webkit-slider-thumb]:rounded-full
                      [&::-webkit-slider-thumb]:bg-amber-400"
                                    />
                                    <span className="font-mono text-amber-400 w-12">{formatTime(loopStart)}</span>
                                </div>

                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-gray-400">Loop End:</span>
                                    <input
                                        type="range"
                                        min={0}
                                        max={duration}
                                        step={0.1}
                                        value={loopEnd}
                                        onChange={handleLoopEndChange}
                                        className="w-32 h-2 bg-gray-700 rounded-full appearance-none cursor-pointer
                      [&::-webkit-slider-thumb]:appearance-none
                      [&::-webkit-slider-thumb]:w-3
                      [&::-webkit-slider-thumb]:h-3
                      [&::-webkit-slider-thumb]:rounded-full
                      [&::-webkit-slider-thumb]:bg-amber-400"
                                    />
                                    <span className="font-mono text-amber-400 w-12">{formatTime(loopEnd)}</span>
                                </div>

                                <span className="text-sm text-gray-500">
                                    Duração: {formatTime(loopEnd - loopStart)}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Waveforms Section */}
            <div className="relative z-10 px-8 mb-4">
                <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-4 border border-white/10">
                    <div className="flex items-center gap-2 mb-4">
                        <Waves className="w-5 h-5 text-purple-400" />
                        <h3 className="text-sm font-bold text-gray-300 tracking-wider">WAVEFORMS</h3>
                    </div>
                    <div className="space-y-2">
                        {project.stems?.filter(stem => stem.type !== StemType.CLICK).map(stem => {
                            const config = stemConfig[stem.type as StemType]
                            const isMuted = mutes[stem.type as StemType] || (hasSoloActive && !solos[stem.type as StemType])
                            return (
                                <div key={stem.type} className="flex items-center gap-3">
                                    <div className="w-24 flex items-center gap-2">
                                        <span className="text-lg">{config?.icon}</span>
                                        <span className={`text-xs font-bold ${config?.textColor}`}>
                                            {config?.label}
                                        </span>
                                    </div>
                                    <div className="flex-1">
                                        <WaveformTrack
                                            url={apiService.getDownloadUrl(stem.url)}
                                            color={config?.hexColor || '#a855f7'}
                                            height={40}
                                            currentTime={currentTime}
                                            duration={duration}
                                            isPlaying={isPlaying}
                                            volume={volumes[stem.type as StemType]}
                                            muted={isMuted}
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>

            {/* Console de Mixagem */}
            <div className="relative z-10 px-8 pb-8">
                <div className="bg-gradient-to-b from-gray-800/80 to-gray-900/80 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-2xl">
                    <div className="text-center mb-8">
                        <h2 className="text-xl font-bold tracking-widest text-gray-300">CONSOLE DE MIXAGEM</h2>
                    </div>

                    <div className="grid grid-cols-4 gap-6">
                        {stemOrder.map(stemType => {
                            const config = stemConfig[stemType]
                            const isMuted = mutes[stemType] || (hasSoloActive && !solos[stemType])

                            return (
                                <div key={stemType}
                                    className={`relative rounded-2xl p-6 bg-gradient-to-b ${config.gradient} border ${config.border} transition-all duration-300 ${isMuted ? 'opacity-50' : 'opacity-100'}`}>
                                    <div className="text-center mb-2">
                                        <span className="text-4xl">{config.icon}</span>
                                    </div>

                                    <h3 className={`text-center font-bold tracking-wider mb-4 ${config.textColor}`}>
                                        {config.label}
                                    </h3>

                                    <div className="flex justify-center gap-2 mb-6">
                                        <button onClick={() => handleMuteToggle(stemType)}
                                            className={`w-10 h-10 rounded-lg font-bold text-sm transition-all ${mutes[stemType] ? 'bg-red-500 text-white shadow-lg shadow-red-500/30' : `${config.buttonColor} text-white hover:opacity-80`}`}>
                                            M
                                        </button>
                                        <button onClick={() => handleSoloToggle(stemType)}
                                            className={`w-10 h-10 rounded-lg font-bold text-sm transition-all ${solos[stemType] ? 'bg-amber-400 text-black shadow-lg shadow-amber-400/30' : 'bg-gray-600 text-gray-300 hover:bg-gray-500'}`}>
                                            S
                                        </button>
                                    </div>

                                    <div className="relative h-48 flex items-center justify-center">
                                        <div className="absolute left-2 top-0 h-full flex flex-col justify-between text-xs text-gray-500">
                                            <span>+12</span>
                                            <span className="mt-4">0</span>
                                            <span className="mt-auto mb-16">-12</span>
                                            <span className="mb-8">-24</span>
                                            <span className="mb-0">-∞</span>
                                        </div>

                                        <div className="relative w-4 h-full rounded-full bg-gray-800 border border-gray-700 overflow-hidden mx-auto">
                                            <div className={`absolute bottom-0 w-full bg-gradient-to-t ${config.faderColor} transition-all duration-100`}
                                                style={{ height: `${volumes[stemType]}%` }} />
                                            <div className="absolute inset-0 flex flex-col justify-between py-1">
                                                {[...Array(25)].map((_, i) => (
                                                    <div key={i} className="w-full h-px bg-gray-700" />
                                                ))}
                                            </div>
                                        </div>

                                        <input
                                            type="range"
                                            min={0}
                                            max={100}
                                            value={volumes[stemType]}
                                            onChange={(e) => handleVolumeChange(stemType, parseInt(e.target.value))}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                            style={{ writingMode: 'vertical-lr', direction: 'rtl' } as any}
                                        />
                                    </div>

                                    <div className={`mt-4 py-2 px-4 rounded-lg bg-black/30 text-center ${config.textColor}`}>
                                        <span className="text-xl font-mono font-bold">{volumes[stemType]}%</span>
                                    </div>
                                </div>
                            )
                        })}
                    </div>

                    <div className="mt-8 pt-6 border-t border-white/10">
                        <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
                            <span>🎵 Key: Transponha a música</span>
                            <span className="text-gray-600">|</span>
                            <span>⚡ Speed: Ajuste a velocidade para praticar</span>
                            <span className="text-gray-600">|</span>
                            <span>🔁 Loop: Repita uma seção específica</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
