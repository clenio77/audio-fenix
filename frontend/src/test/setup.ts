/**
 * Test Setup - Vitest
 * 
 * Configuração global para os testes do frontend.
 */
import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll, vi } from 'vitest'

// Mock do ResizeObserver (necessário para RadixUI components)
class ResizeObserverMock {
    observe() { }
    unobserve() { }
    disconnect() { }
}

// Mock do matchMedia (necessário para alguns componentes)
beforeAll(() => {
    // ResizeObserver mock
    (window as any).ResizeObserver = ResizeObserverMock

    // PointerEvent mock (necessário para RadixUI Slider)
    class PointerEventMock extends Event {
        pointerId: number = 0
        pressure: number = 0
        tangentialPressure: number = 0
        tiltX: number = 0
        tiltY: number = 0
        twist: number = 0
        width: number = 0
        height: number = 0
        pointerType: string = 'mouse'
        isPrimary: boolean = true

        constructor(type: string, params?: any) {
            super(type, params)
        }

        getCoalescedEvents() { return [] }
        getPredictedEvents() { return [] }
    }

    (window as any).PointerEvent = PointerEventMock

    // matchMedia mock
    Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation((query: string) => ({
            matches: false,
            media: query,
            onchange: null,
            addListener: vi.fn(),
            removeListener: vi.fn(),
            addEventListener: vi.fn(),
            removeEventListener: vi.fn(),
            dispatchEvent: vi.fn(),
        })),
    })

    // Element.prototype mock para RadixUI
    if (!Element.prototype.hasPointerCapture) {
        Element.prototype.hasPointerCapture = () => false
    }
    if (!Element.prototype.setPointerCapture) {
        Element.prototype.setPointerCapture = () => { }
    }
    if (!Element.prototype.releasePointerCapture) {
        Element.prototype.releasePointerCapture = () => { }
    }
})

// Limpar mocks após cada teste
afterEach(() => {
    vi.clearAllMocks()
})

// Limpar tudo após todos os testes
afterAll(() => {
    vi.restoreAllMocks()
})

