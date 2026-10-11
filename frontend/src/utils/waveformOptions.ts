/**
 * Options for visualization-only WaveSurfer instances in the mixer.
 *
 * Must NOT use backend: 'WebAudio'. That path constructs a permanent
 * AudioContext per track that WaveSurfer never closes on destroy, so
 * opening a few projects exhausts the browser AudioContext quota and
 * breaks playback.
 */
export interface WaveformVisualOptionsInput {
    container: HTMLElement
    color: string
    height: number
}

export function buildWaveformVisualOptions({
    container,
    color,
    height,
}: WaveformVisualOptionsInput) {
    return {
        container,
        waveColor: color + '60',
        progressColor: color,
        cursorColor: '#fff',
        cursorWidth: 2,
        height,
        barWidth: 2,
        barGap: 1,
        barRadius: 2,
        normalize: true,
        interact: false,
        hideScrollbar: true,
        mediaControls: false,
    }
}
