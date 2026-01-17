/**
 * SpeedControl Component - Frontend
 * 
 * Controle visual de velocidade com:
 * - Presets rápidos (0.5x, 0.75x, 1x, 1.25x, 1.5x)
 * - Slider fino
 * - Indicador de porcentagem
 */
import { Gauge, Minus, Plus, RotateCcw } from 'lucide-react'

interface SpeedControlProps {
    speed: number // 0.5 a 1.5
    onChange: (speed: number) => void
    disabled?: boolean
}

const PRESETS = [
    { value: 0.5, label: '0.5x' },
    { value: 0.75, label: '0.75x' },
    { value: 1.0, label: '1x' },
    { value: 1.25, label: '1.25x' },
    { value: 1.5, label: '1.5x' },
]

export default function SpeedControl({ speed, onChange, disabled = false }: SpeedControlProps) {
    const handleIncrement = () => {
        if (!disabled) {
            const newSpeed = Math.min(1.5, +(speed + 0.05).toFixed(2))
            onChange(newSpeed)
        }
    }

    const handleDecrement = () => {
        if (!disabled) {
            const newSpeed = Math.max(0.5, +(speed - 0.05).toFixed(2))
            onChange(newSpeed)
        }
    }

    const handleReset = () => {
        if (!disabled) {
            onChange(1.0)
        }
    }

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!disabled) {
            onChange(parseFloat(e.target.value))
        }
    }

    const handlePresetClick = (value: number) => {
        if (!disabled) {
            onChange(value)
        }
    }

    // Cor baseada na velocidade
    const getColor = () => {
        if (speed === 1) return 'emerald'
        if (speed < 1) return 'blue'
        return 'orange'
    }

    const color = getColor()
    const colorClasses = {
        emerald: {
            bg: 'bg-emerald-500',
            text: 'text-emerald-400',
            border: 'border-emerald-500/30',
            glow: 'shadow-emerald-500/30',
            gradient: 'from-emerald-600/20 to-green-600/20',
        },
        blue: {
            bg: 'bg-blue-500',
            text: 'text-blue-400',
            border: 'border-blue-500/30',
            glow: 'shadow-blue-500/30',
            gradient: 'from-blue-600/20 to-cyan-600/20',
        },
        orange: {
            bg: 'bg-orange-500',
            text: 'text-orange-400',
            border: 'border-orange-500/30',
            glow: 'shadow-orange-500/30',
            gradient: 'from-orange-600/20 to-red-600/20',
        },
    }

    const styles = colorClasses[color]
    const percentage = Math.round(speed * 100)

    return (
        <div className={`bg-gradient-to-r ${styles.gradient} backdrop-blur-xl rounded-2xl p-4 border ${styles.border} transition-all duration-300`}>
            <div className="flex items-center justify-between gap-4">
                {/* Label */}
                <div className="flex items-center gap-2">
                    <Gauge className={`w-5 h-5 ${styles.text}`} />
                    <span className="text-sm font-medium text-gray-300">SPEED</span>
                </div>

                {/* Controls */}
                <div className="flex items-center gap-3">
                    {/* Decrement */}
                    <button
                        onClick={handleDecrement}
                        disabled={disabled || speed <= 0.5}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Diminuir velocidade"
                    >
                        <Minus className="w-4 h-4 text-gray-400" />
                    </button>

                    {/* Display */}
                    <div className={`relative px-6 py-3 bg-black/50 rounded-xl border ${styles.border} min-w-[120px] text-center shadow-lg ${styles.glow}`}>
                        <div className="flex items-center justify-center gap-1">
                            <span className={`text-2xl font-bold ${styles.text} font-mono`}>
                                {speed.toFixed(2)}
                            </span>
                            <span className={`text-lg ${styles.text} opacity-80`}>x</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                            {percentage}%
                        </div>
                    </div>

                    {/* Increment */}
                    <button
                        onClick={handleIncrement}
                        disabled={disabled || speed >= 1.5}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Aumentar velocidade"
                    >
                        <Plus className="w-4 h-4 text-gray-400" />
                    </button>

                    {/* Reset */}
                    <button
                        onClick={handleReset}
                        disabled={disabled || speed === 1}
                        className={`p-2 rounded-lg transition-all ${speed !== 1
                                ? 'bg-white/10 hover:bg-white/20 text-white'
                                : 'bg-white/5 text-gray-600 cursor-not-allowed'
                            }`}
                        title="Resetar para 1x"
                    >
                        <RotateCcw className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Presets */}
            <div className="mt-4 flex justify-center gap-2">
                {PRESETS.map((preset) => (
                    <button
                        key={preset.value}
                        onClick={() => handlePresetClick(preset.value)}
                        disabled={disabled}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${Math.abs(speed - preset.value) < 0.01
                                ? `${styles.bg} text-white shadow-lg ${styles.glow}`
                                : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {preset.label}
                    </button>
                ))}
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
                                width: `${((speed - 0.5) / 1) * 100}%`,
                            }}
                        />
                    </div>

                    {/* Hidden input for interaction */}
                    <input
                        type="range"
                        min={0.5}
                        max={1.5}
                        step={0.01}
                        value={speed}
                        onChange={handleSliderChange}
                        disabled={disabled}
                        className="absolute inset-0 w-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    />
                </div>
            </div>

            {/* Info text */}
            <div className="mt-4 text-xs text-center text-gray-500">
                {speed === 1 ? (
                    <span>Velocidade original</span>
                ) : speed < 1 ? (
                    <span>🐢 {Math.round((1 - speed) * 100)}% mais lento - ideal para praticar</span>
                ) : (
                    <span>⚡ {Math.round((speed - 1) * 100)}% mais rápido</span>
                )}
            </div>
        </div>
    )
}
