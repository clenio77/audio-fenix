/**
 * PitchControl Component - Frontend
 * 
 * Controle visual de pitch com:
 * - Display de notas musicais
 * - Slider horizontal
 * - Botões incrementais
 */
import { Music, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react'

interface PitchControlProps {
    pitch: number // -12 a +12 semitons
    onChange: (pitch: number) => void
    disabled?: boolean
}

const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

export default function PitchControl({ pitch, onChange, disabled = false }: PitchControlProps) {
    const getNoteFromPitch = (semitones: number): string => {
        const baseIndex = 0 // C
        const index = (baseIndex + semitones + 12) % 12
        return NOTES[index]
    }

    const getSign = (value: number): string => {
        if (value > 0) return '+'
        if (value < 0) return ''
        return ''
    }

    const handleIncrement = () => {
        if (!disabled && pitch < 12) {
            onChange(pitch + 1)
        }
    }

    const handleDecrement = () => {
        if (!disabled && pitch > -12) {
            onChange(pitch - 1)
        }
    }

    const handleReset = () => {
        if (!disabled) {
            onChange(0)
        }
    }

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!disabled) {
            onChange(parseInt(e.target.value))
        }
    }

    // Cor baseada no pitch
    const getColor = () => {
        if (pitch === 0) return 'cyan'
        if (pitch > 0) return 'amber'
        return 'purple'
    }

    const color = getColor()
    const colorClasses = {
        cyan: {
            bg: 'bg-cyan-500',
            text: 'text-cyan-400',
            border: 'border-cyan-500/30',
            glow: 'shadow-cyan-500/30',
            gradient: 'from-cyan-600/20 to-blue-600/20',
        },
        amber: {
            bg: 'bg-amber-500',
            text: 'text-amber-400',
            border: 'border-amber-500/30',
            glow: 'shadow-amber-500/30',
            gradient: 'from-amber-600/20 to-orange-600/20',
        },
        purple: {
            bg: 'bg-purple-500',
            text: 'text-purple-400',
            border: 'border-purple-500/30',
            glow: 'shadow-purple-500/30',
            gradient: 'from-purple-600/20 to-violet-600/20',
        },
    }

    const styles = colorClasses[color]

    return (
        <div className={`bg-gradient-to-r ${styles.gradient} backdrop-blur-xl rounded-2xl p-4 border ${styles.border} transition-all duration-300`}>
            <div className="flex items-center justify-between gap-4">
                {/* Label */}
                <div className="flex items-center gap-2">
                    <Music className={`w-5 h-5 ${styles.text}`} />
                    <span className="text-sm font-medium text-gray-300">KEY / PITCH</span>
                </div>

                {/* Controls */}
                <div className="flex items-center gap-3">
                    {/* Decrement */}
                    <button
                        onClick={handleDecrement}
                        disabled={disabled || pitch <= -12}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Diminuir 1 semitom"
                    >
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                    </button>

                    {/* Display */}
                    <div className={`relative px-6 py-3 bg-black/50 rounded-xl border ${styles.border} min-w-[140px] text-center shadow-lg ${styles.glow}`}>
                        <div className="flex items-center justify-center gap-2">
                            <span className={`text-2xl font-bold ${styles.text} font-mono`}>
                                {getNoteFromPitch(pitch)}
                            </span>
                            <span className={`text-sm ${styles.text} opacity-80`}>
                                ({getSign(pitch)}{pitch})
                            </span>
                        </div>

                        {/* Indicador visual de direção */}
                        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5">
                            {[...Array(Math.abs(pitch))].map((_, i) => (
                                <div
                                    key={i}
                                    className={`w-1.5 h-1.5 rounded-full ${styles.bg} opacity-${Math.min(100, 50 + i * 10)}`}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Increment */}
                    <button
                        onClick={handleIncrement}
                        disabled={disabled || pitch >= 12}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Aumentar 1 semitom"
                    >
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                    </button>

                    {/* Reset */}
                    <button
                        onClick={handleReset}
                        disabled={disabled || pitch === 0}
                        className={`p-2 rounded-lg transition-all ${pitch !== 0
                                ? 'bg-white/10 hover:bg-white/20 text-white'
                                : 'bg-white/5 text-gray-600 cursor-not-allowed'
                            }`}
                        title="Resetar para C (0)"
                    >
                        <RotateCcw className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Slider */}
            <div className="mt-4">
                <div className="relative">
                    {/* Track background */}
                    <div className="h-2 bg-gray-800 rounded-full">
                        {/* Filled track */}
                        <div
                            className={`h-full rounded-full ${styles.bg} transition-all duration-100`}
                            style={{
                                width: `${((pitch + 12) / 24) * 100}%`,
                            }}
                        />
                    </div>

                    {/* Tick marks */}
                    <div className="absolute top-4 w-full flex justify-between px-0.5">
                        {['-12', '-6', '0', '+6', '+12'].map((label, i) => (
                            <span key={i} className="text-xs text-gray-600">{label}</span>
                        ))}
                    </div>

                    {/* Hidden input for interaction */}
                    <input
                        type="range"
                        min={-12}
                        max={12}
                        value={pitch}
                        onChange={handleSliderChange}
                        disabled={disabled}
                        className="absolute inset-0 w-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    />
                </div>
            </div>

            {/* Info text */}
            <div className="mt-6 text-xs text-center text-gray-500">
                {pitch === 0 ? (
                    <span>Tom original</span>
                ) : pitch > 0 ? (
                    <span>🔺 {pitch} semitom{pitch !== 1 ? 's' : ''} acima do original</span>
                ) : (
                    <span>🔻 {Math.abs(pitch)} semitom{pitch !== -1 ? 's' : ''} abaixo do original</span>
                )}
            </div>
        </div>
    )
}
