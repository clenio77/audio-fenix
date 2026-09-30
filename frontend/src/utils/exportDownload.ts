/**
 * Open an export download without losing the user-gesture → popup chain.
 *
 * `window.open` after `await exportMix(...)` is blocked by browsers once the
 * click activation expires, so Exportar Mix can succeed on the server while
 * the client never receives a file and shows no error.
 */

export function openExportDownloadWindow(): Window | null {
    if (typeof window === 'undefined') return null
    return window.open('about:blank', '_blank')
}

export function navigateExportDownload(
    downloadWindow: Window | null,
    url: string,
): void {
    if (downloadWindow && !downloadWindow.closed) {
        downloadWindow.location.href = url
        return
    }

    // Popup was blocked at gesture time — fall back to a top-level navigation
    // attempt so the user still gets the file somehow.
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.target = '_blank'
    anchor.rel = 'noopener noreferrer'
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
}

export function closeExportDownloadWindow(downloadWindow: Window | null): void {
    if (downloadWindow && !downloadWindow.closed) {
        downloadWindow.close()
    }
}
