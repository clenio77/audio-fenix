import { describe, it, expect } from 'vitest'
import { StemType } from '@/types'
import { getEffectiveVolume } from '../stemPlayback'

const baseVolumes = {
    [StemType.VOCALS]: 100,
    [StemType.DRUMS]: 100,
    [StemType.BASS]: 100,
    [StemType.OTHER]: 100,
    [StemType.CLICK]: 50,
    [StemType.MIDI]: 0,
    [StemType.SCORE]: 0,
}

const unmuted = {
    [StemType.VOCALS]: false,
    [StemType.DRUMS]: false,
    [StemType.BASS]: false,
    [StemType.OTHER]: false,
    [StemType.CLICK]: false,
    [StemType.MIDI]: true,
    [StemType.SCORE]: true,
}

const noSolo = {
    [StemType.VOCALS]: false,
    [StemType.DRUMS]: false,
    [StemType.BASS]: false,
    [StemType.OTHER]: false,
    [StemType.CLICK]: false,
    [StemType.MIDI]: false,
    [StemType.SCORE]: false,
}

describe('getEffectiveVolume', () => {
    it('applies default click mute as silence (mount-time mixer defaults)', () => {
        const mutes = { ...unmuted, [StemType.CLICK]: true }
        expect(getEffectiveVolume(StemType.CLICK, baseVolumes, mutes, noSolo)).toBe(0)
    })

    it('scales unmuted click by fader percent', () => {
        expect(getEffectiveVolume(StemType.CLICK, baseVolumes, unmuted, noSolo)).toBe(0.5)
    })

    it('silences non-soloed stems when any solo is active', () => {
        const solos = { ...noSolo, [StemType.VOCALS]: true }
        expect(getEffectiveVolume(StemType.DRUMS, baseVolumes, unmuted, solos)).toBe(0)
        expect(getEffectiveVolume(StemType.VOCALS, baseVolumes, unmuted, solos)).toBe(1)
    })

    it('keeps explicit mute even when that stem is soloed', () => {
        const mutes = { ...unmuted, [StemType.VOCALS]: true }
        const solos = { ...noSolo, [StemType.VOCALS]: true }
        expect(getEffectiveVolume(StemType.VOCALS, baseVolumes, mutes, solos)).toBe(0)
    })
})
