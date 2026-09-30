import { describe, it, expect } from 'vitest'
import { formatApiErrorDetail } from '../apiError'

describe('formatApiErrorDetail', () => {
    it('returns string details unchanged', () => {
        expect(formatApiErrorDetail('Email ou senha incorretos')).toBe(
            'Email ou senha incorretos',
        )
    })

    it('joins FastAPI 422 validation error messages', () => {
        const detail = [
            {
                type: 'value_error',
                loc: ['body', 'email'],
                msg: 'value is not a valid email address',
                input: 'foo@bar',
            },
        ]

        expect(formatApiErrorDetail(detail)).toBe(
            'value is not a valid email address',
        )
    })

    it('joins multiple validation messages', () => {
        const detail = [
            { msg: 'String should have at most 100 characters' },
            { msg: 'value is not a valid email address' },
        ]

        expect(formatApiErrorDetail(detail)).toBe(
            'String should have at most 100 characters; value is not a valid email address',
        )
    })

    it('uses fallback for empty / unknown payloads', () => {
        expect(formatApiErrorDetail(undefined)).toBe('Erro ao processar solicitação')
        expect(formatApiErrorDetail(null)).toBe('Erro ao processar solicitação')
        expect(formatApiErrorDetail({})).toBe('Erro ao processar solicitação')
        expect(formatApiErrorDetail('   ')).toBe('Erro ao processar solicitação')
        expect(formatApiErrorDetail([], 'Custom')).toBe('Custom')
    })
})
