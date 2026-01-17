/**
 * Mixer Channel Component - Frontend
 * 
 * Componente que representa um canal individual do mixer.
 */
import { StemType } from '@/types'
import * as Slider from '@radix-ui/react-slider'

interface MixerChannelProps {
    stemType: StemType
    volume: number
    muted: boolean
    solo: boolean
    color: string
    onVolumeChange: (value: number) => void
    onMuteToggle: () => void
    onSoloToggle: () => void
}

export default function MixerChannel({
    stemType,
    volume,
    muted,
    solo,
    color,
    onVolumeChange,
    onMuteToggle,
    onSoloToggle,
}: MixerChannelProps) {
    const labels: Record<StemType, string> = {
        [StemType.VOCALS]: 'Vocal',
        [StemType.DRUMS]: 'Bateria',
        [StemType.BASS]: 'Baixo',
        [StemType.OTHER]: 'Outros',
        [StemType.CLICK]: 'Click',
    }

    const icons: Record<StemType, string> = {
        [StemType.VOCALS]: '🎤',
        [StemType.DRUMS]: '🥁',
        [StemType.BASS]: '🎸',
        [StemType.OTHER]: '🎹',
        [StemType.CLICK]: '🎵',
    }

    return (
        <div className="mixer-channel">
            {/* Nome do Canal */}
            <div className="text-center mb-4">
                <div className="text-3xl mb-2">{icons[stemType]}</div>
                <span className={`font-bold uppercase text-sm ${color}`}>
                    {labels[stemType]}
                </span>
            </div>

            {/* Botões de Controle */}
            <div className="flex gap-2 mb-6 justify-center">
                <button
                    onClick={onMuteToggle}
                    className={`mixer-button-mute ${muted ? 'active' : ''}`}
                    title="Mute"
                >
                    M
                </button>
                <button
                    onClick={onSoloToggle}
                    className={`mixer-button-solo ${solo ? 'active' : ''}`}
                    title="Solo"
                >
                    S
                </button>
            </div>

            {/* Fader de Volume (Vertical) */}
            <div className="flex-1 flex flex-col items-center mb-4">
                <Slider.Root
                    className="relative flex items-center select-none touch-none h-64 w-6"
                    value={[volume]}
                    max={100}
                    step={1}
                    orientation="vertical"
                    onValueChange={(values: number[]) => onVolumeChange(values[0])}
                >
                    <Slider.Track className="bg-mixer-fader relative grow rounded-full w-2">
                        <Slider.Range className={`absolute ${color.replace('text-', 'bg-')} rounded-full w-full`} />
                    </Slider.Track>
                    <Slider.Thumb
                        className="block w-6 h-6 bg-mixer-accent shadow-lg rounded-full hover:scale-110 focus:outline-none focus:ring-2 focus:ring-mixer-accent transition-transform cursor-grab active:cursor-grabbing"
                        aria-label="Volume"
                    />
                </Slider.Root>

                {/* Indicador de Volume */}
                <div className="mt-3 text-center">
                    <span className="text-sm font-mono text-gray-400">{volume}%</span>
                </div>
            </div>

            {/* Waveform Placeholder */}
            <div className="waveform-container">
                <div className="w-full h-full flex items-center justify-center text-gray-600 text-xs">
                    Waveform
                </div>
            </div>
        </div>
    )
}
