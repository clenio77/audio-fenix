import { describe, it, expect } from 'vitest'
import { classifyStatusPollError } from '../statusPoll'

describe('classifyStatusPollError', () => {
    it('stops polling on 410 Gone (expired project)', () => {
        const outcome = classifyStatusPollError({ response: { status: 410 } })
        expect(outcome.kind).toBe('stop')
        if (outcome.kind === 'stop') {
            expect(outcome.message.toLowerCase()).toContain('expirou')
        }
    })

    it('stops polling on 404 Not Found', () => {
        const outcome = classifyStatusPollError({ response: { status: 404 } })
        expect(outcome.kind).toBe('stop')
        if (outcome.kind === 'stop') {
            expect(outcome.message.toLowerCase()).toContain('não encontrado')
        }
    })

    it('keeps polling on transient network errors', () => {
        expect(classifyStatusPollError(new Error('Network Error')).kind).toBe('continue')
        expect(classifyStatusPollError({ response: { status: 500 } }).kind).toBe('continue')
        expect(classifyStatusPollError({ response: { status: 503 } }).kind).toBe('continue')
        expect(classifyStatusPollError(null).kind).toBe('continue')
    })
})
