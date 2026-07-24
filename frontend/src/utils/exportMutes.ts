import { StemType } from '@/types'

/**
 * Build the mute map sent to POST /api/export so the file matches what the
 * mixer plays. Solo must silence every non-soloed stem even when that stem's
 * mute toggle is off.
 */
export function buildExportMutes(
    mutes: Record<StemType, boolean>,
    solos: Record<StemType, boolean>,
): Record<StemType, boolean> {
    const hasSoloActive = Object.values(solos).some(Boolean)

    return (Object.keys(mutes) as StemType[]).reduce(
        (acc, stem) => {
            acc[stem] = Boolean(mutes[stem]) || (hasSoloActive && !solos[stem])
            return acc
        },
        {} as Record<StemType, boolean>,
    )
}
