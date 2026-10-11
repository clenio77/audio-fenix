import { describe, it, expect } from 'vitest'
import { buildWaveformVisualOptions } from '../waveformOptions'

describe('buildWaveformVisualOptions', () => {
    const container = {} as HTMLElement

    it('omits WebAudio backend so tracks do not leak AudioContexts', () => {
        const options = buildWaveformVisualOptions({
            container,
            color: '#ec4899',
            height: 40,
        })

        expect(options).not.toHaveProperty('backend')
        expect((options as { backend?: string }).backend).toBeUndefined()
    })

    it('keeps visualization styling and disables interaction', () => {
        const options = buildWaveformVisualOptions({
            container,
            color: '#22c55e',
            height: 50,
        })

        expect(options.container).toBe(container)
        expect(options.waveColor).toBe('#22c55e60')
        expect(options.progressColor).toBe('#22c55e')
        expect(options.height).toBe(50)
        expect(options.interact).toBe(false)
        expect(options.mediaControls).toBe(false)
        expect(options.normalize).toBe(true)
    })
})
