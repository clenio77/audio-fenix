/**
 * Status poll ordering — reject stale responses after READY/FAILED.
 */
import { describe, it, expect } from 'vitest'
import { ProjectStatus } from '@/types'
import { isTerminalProjectStatus, shouldAcceptPolledStatus } from '../statusPoll'

describe('isTerminalProjectStatus', () => {
    it('treats READY and FAILED as terminal', () => {
        expect(isTerminalProjectStatus(ProjectStatus.READY)).toBe(true)
        expect(isTerminalProjectStatus(ProjectStatus.FAILED)).toBe(true)
        expect(isTerminalProjectStatus('ready')).toBe(true)
        expect(isTerminalProjectStatus('failed')).toBe(true)
    })

    it('treats pending/processing as non-terminal', () => {
        expect(isTerminalProjectStatus(ProjectStatus.PENDING)).toBe(false)
        expect(isTerminalProjectStatus(ProjectStatus.PROCESSING)).toBe(false)
    })
})

describe('shouldAcceptPolledStatus', () => {
    it('accepts the first status when nothing is loaded yet', () => {
        expect(shouldAcceptPolledStatus(null, ProjectStatus.PROCESSING)).toBe(true)
        expect(shouldAcceptPolledStatus(undefined, ProjectStatus.READY)).toBe(true)
    })

    it('allows pending → processing → ready progression', () => {
        expect(shouldAcceptPolledStatus(ProjectStatus.PENDING, ProjectStatus.PROCESSING)).toBe(true)
        expect(shouldAcceptPolledStatus(ProjectStatus.PROCESSING, ProjectStatus.READY)).toBe(true)
        expect(shouldAcceptPolledStatus(ProjectStatus.PROCESSING, ProjectStatus.FAILED)).toBe(true)
    })

    it('rejects stale PROCESSING after READY (empty-mixer race)', () => {
        expect(shouldAcceptPolledStatus(ProjectStatus.READY, ProjectStatus.PROCESSING)).toBe(false)
        expect(shouldAcceptPolledStatus(ProjectStatus.READY, ProjectStatus.PENDING)).toBe(false)
        expect(shouldAcceptPolledStatus(ProjectStatus.READY, ProjectStatus.FAILED)).toBe(false)
    })

    it('rejects regressions after FAILED', () => {
        expect(shouldAcceptPolledStatus(ProjectStatus.FAILED, ProjectStatus.PROCESSING)).toBe(false)
        expect(shouldAcceptPolledStatus(ProjectStatus.FAILED, ProjectStatus.READY)).toBe(false)
    })

    it('allows identical terminal re-polls (refresh stems/message)', () => {
        expect(shouldAcceptPolledStatus(ProjectStatus.READY, ProjectStatus.READY)).toBe(true)
        expect(shouldAcceptPolledStatus(ProjectStatus.FAILED, ProjectStatus.FAILED)).toBe(true)
    })
})
