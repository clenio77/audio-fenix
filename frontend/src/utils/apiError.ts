/**
 * Normalize FastAPI / axios error payloads into a renderable string.
 *
 * FastAPI returns `detail` as a string for HTTPException, but as an array of
 * `{ loc, msg, type }` objects for request validation (HTTP 422). Rendering the
 * array as a React child throws and white-screens the page.
 */
export function formatApiErrorDetail(
    detail: unknown,
    fallback = 'Erro ao processar solicitação',
): string {
    if (typeof detail === 'string') {
        const trimmed = detail.trim()
        return trimmed || fallback
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((item) => {
                if (typeof item === 'string') {
                    return item
                }
                if (
                    item &&
                    typeof item === 'object' &&
                    'msg' in item &&
                    typeof (item as { msg: unknown }).msg === 'string'
                ) {
                    return (item as { msg: string }).msg
                }
                return null
            })
            .filter((msg): msg is string => Boolean(msg))

        if (messages.length > 0) {
            return messages.join('; ')
        }
    }

    return fallback
}
