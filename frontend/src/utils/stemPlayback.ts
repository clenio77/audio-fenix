import { StemType } from '@/types'

/**
 * Linear gain (0–1) for a stem, matching mixer mute/solo/volume UI.
 * Mute or an active solo on another stem yields 0.
 */
export function getEffectiveVolume(
    stem: StemType,
    volumes: Record<StemType, number>,
    mutes: Record<StemType, boolean>,
    solos: Record<StemType, boolean>,
): number {
    const hasSoloActive = Object.values(solos).some(Boolean)
    const isMuted = Boolean(mutes[stem]) || (hasSoloActive && !solos[stem])
    if (isMuted) return 0
    return (volumes[stem] ?? 100) / 100
}
