/**
 * Classify project status poll failures.
 *
 * Terminal HTTP errors (expired / not found) must stop the mixer loading
 * poll; transient network failures should keep polling while processing.
 */
export type StatusPollOutcome =
    | { kind: 'continue' }
    | { kind: 'stop'; message: string }

export function classifyStatusPollError(error: unknown): StatusPollOutcome {
    const status = (error as { response?: { status?: number } })?.response?.status

    if (status === 410) {
        return {
            kind: 'stop',
            message: 'Este projeto expirou e não está mais disponível.',
        }
    }

    if (status === 404) {
        return {
            kind: 'stop',
            message: 'Projeto não encontrado.',
        }
    }

    return { kind: 'continue' }
}
