import { afterEach, describe, expect, it, vi } from 'vitest'
import {
    closeExportDownloadWindow,
    navigateExportDownload,
    openExportDownloadWindow,
} from '../exportDownload'

describe('exportDownload', () => {
    afterEach(() => {
        vi.restoreAllMocks()
        document.body.innerHTML = ''
    })

    it('opens a blank window while the user gesture is still active', () => {
        const fakeWin = { closed: false, location: { href: '' }, close: vi.fn() }
        const openSpy = vi.spyOn(window, 'open').mockReturnValue(fakeWin as unknown as Window)

        const win = openExportDownloadWindow()

        expect(openSpy).toHaveBeenCalledWith('about:blank', '_blank')
        expect(win).toBe(fakeWin)
    })

    it('navigates the pre-opened window to the download URL', () => {
        const fakeWin = { closed: false, location: { href: '' }, close: vi.fn() }

        navigateExportDownload(
            fakeWin as unknown as Window,
            'http://localhost:8000/api/download/export/p/mix.mp3',
        )

        expect(fakeWin.location.href).toBe(
            'http://localhost:8000/api/download/export/p/mix.mp3',
        )
    })

    it('falls back to a blank-target anchor when no window was opened', () => {
        const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

        navigateExportDownload(null, 'http://localhost:8000/api/download/export/p/mix.mp3')

        expect(clickSpy).toHaveBeenCalledTimes(1)
        expect(document.body.querySelector('a')).toBeNull()
    })

    it('falls back when the pre-opened window was already closed', () => {
        const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
        const fakeWin = { closed: true, location: { href: '' }, close: vi.fn() }

        navigateExportDownload(
            fakeWin as unknown as Window,
            'http://localhost:8000/api/download/export/p/mix.mp3',
        )

        expect(fakeWin.location.href).toBe('')
        expect(clickSpy).toHaveBeenCalledTimes(1)
    })

    it('closes the blank window on export failure', () => {
        const close = vi.fn()
        const fakeWin = { closed: false, location: { href: '' }, close }

        closeExportDownloadWindow(fakeWin as unknown as Window)

        expect(close).toHaveBeenCalled()
    })

    it('is a no-op when the window was never opened', () => {
        expect(() => closeExportDownloadWindow(null)).not.toThrow()
    })
})
