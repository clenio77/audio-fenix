/**
 * Auth Service — refresh eligibility
 *
 * Locks the guard that prevents an infinite 401→refresh loop when
 * /refresh itself fails (expired/invalid refresh token).
 */
import { describe, it, expect } from 'vitest'
import { isTokenRefreshEligible } from '../authService'

describe('isTokenRefreshEligible', () => {
    it('allows refresh for protected auth endpoints', () => {
        expect(isTokenRefreshEligible('/me')).toBe(true)
        expect(isTokenRefreshEligible('/logout')).toBe(true)
        expect(isTokenRefreshEligible('/change-password')).toBe(true)
        expect(isTokenRefreshEligible('http://localhost:8000/api/auth/me')).toBe(true)
    })

    it('blocks refresh for login, register, and refresh itself', () => {
        expect(isTokenRefreshEligible('/refresh')).toBe(false)
        expect(isTokenRefreshEligible('/login')).toBe(false)
        expect(isTokenRefreshEligible('/register')).toBe(false)
        expect(isTokenRefreshEligible('http://localhost:8000/api/auth/refresh')).toBe(false)
        expect(isTokenRefreshEligible('http://localhost:8000/api/auth/login')).toBe(false)
        expect(isTokenRefreshEligible('http://localhost:8000/api/auth/register')).toBe(false)
    })

    it('rejects missing urls', () => {
        expect(isTokenRefreshEligible(undefined)).toBe(false)
        expect(isTokenRefreshEligible('')).toBe(false)
    })
})
