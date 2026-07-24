import { describe, it, expect } from 'vitest'
import { StemType } from '@/types'
import { buildExportMutes } from '../exportMutes'

const allUnmuted: Record<StemType, boolean> = {
    [StemType.VOCALS]: false,
    [StemType.DRUMS]: false,
    [StemType.BASS]: false,
    [StemType.OTHER]: false,
    [StemType.CLICK]: true,
    [StemType.MIDI]: true,
    [StemType.SCORE]: true,
}

const noSolos: Record<StemType, boolean> = {
    [StemType.VOCALS]: false,
    [StemType.DRUMS]: false,
    [StemType.BASS]: false,
    [StemType.OTHER]: false,
    [StemType.CLICK]: false,
    [StemType.MIDI]: false,
    [StemType.SCORE]: false,
}

describe('buildExportMutes', () => {
    it('passes through mute toggles when no stem is soloed', () => {
        expect(buildExportMutes(allUnmuted, noSolos)).toEqual(allUnmuted)
    })

    it('silences non-soloed stems so export matches the player', () => {
        const solos = { ...noSolos, [StemType.VOCALS]: true }

        const result = buildExportMutes(allUnmuted, solos)

        expect(result[StemType.VOCALS]).toBe(false)
        expect(result[StemType.DRUMS]).toBe(true)
        expect(result[StemType.BASS]).toBe(true)
        expect(result[StemType.OTHER]).toBe(true)
        expect(result[StemType.CLICK]).toBe(true)
    })

    it('keeps an explicitly muted stem muted even when solo is active on another', () => {
        const mutes = { ...allUnmuted, [StemType.DRUMS]: true }
        const solos = { ...noSolos, [StemType.VOCALS]: true }

        const result = buildExportMutes(mutes, solos)

        expect(result[StemType.DRUMS]).toBe(true)
        expect(result[StemType.VOCALS]).toBe(false)
    })

    it('allows multiple solos (only non-soloed stems are forced mute)', () => {
        const solos = {
            ...noSolos,
            [StemType.VOCALS]: true,
            [StemType.BASS]: true,
        }

        const result = buildExportMutes(allUnmuted, solos)

        expect(result[StemType.VOCALS]).toBe(false)
        expect(result[StemType.BASS]).toBe(false)
        expect(result[StemType.DRUMS]).toBe(true)
        expect(result[StemType.OTHER]).toBe(true)
    })
})
