/**
 * Status polling helpers for MixerPage.
 *
 * Overlapping GET /api/status calls can return out of order. A late
 * PROCESSING/PENDING response must not overwrite READY/FAILED (which
 * drops stems and leaves the mixer empty with polling already stopped).
 */
import { ProjectStatus } from '@/types'

export function isTerminalProjectStatus(status: ProjectStatus | string): boolean {
    return status === ProjectStatus.READY || status === ProjectStatus.FAILED
}

/**
 * Whether an incoming poll result should replace the current project status.
 * Terminal statuses are sticky: once READY or FAILED, reject any other status.
 */
export function shouldAcceptPolledStatus(
    current: ProjectStatus | string | null | undefined,
    incoming: ProjectStatus | string,
): boolean {
    if (current == null) return true
    if (isTerminalProjectStatus(current) && incoming !== current) {
        return false
    }
    return true
}
