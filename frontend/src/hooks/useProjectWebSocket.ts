/**
 * Hook useProjectWebSocket - Frontend
 * 
 * Hook para conexão WebSocket com status do projeto em tempo real.
 */
import { useEffect, useRef, useState, useCallback } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

interface ProjectStatus {
    type: string
    project_id: string
    status: 'pending' | 'processing' | 'ready' | 'failed'
    progress: number
    message: string
    error?: string
}

interface UseProjectWebSocketProps {
    projectId: string
    onStatusUpdate?: (status: ProjectStatus) => void
    onConnected?: () => void
    onDisconnected?: () => void
    onError?: (error: Event) => void
    enabled?: boolean
}

interface UseProjectWebSocketReturn {
    isConnected: boolean
    lastStatus: ProjectStatus | null
    send: (message: object) => void
    reconnect: () => void
}

export const useProjectWebSocket = ({
    projectId,
    onStatusUpdate,
    onConnected,
    onDisconnected,
    onError,
    enabled = true,
}: UseProjectWebSocketProps): UseProjectWebSocketReturn => {
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const [isConnected, setIsConnected] = useState(false)
    const [lastStatus, setLastStatus] = useState<ProjectStatus | null>(null)
    const reconnectAttempts = useRef(0)
    const maxReconnectAttempts = 5
    const reconnectDelay = 3000

    const connect = useCallback(() => {
        if (!enabled || !projectId) return

        // Limpar conexão anterior
        if (wsRef.current) {
            wsRef.current.close()
        }

        try {
            const ws = new WebSocket(`${WS_URL}/ws/project/${projectId}`)

            ws.onopen = () => {
                console.log(`[WS] Conectado ao projeto ${projectId}`)
                setIsConnected(true)
                reconnectAttempts.current = 0
                onConnected?.()
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as ProjectStatus
                    console.log(`[WS] Mensagem recebida:`, data)

                    if (data.type === 'project_status') {
                        setLastStatus(data)
                        onStatusUpdate?.(data)
                    }
                } catch (e) {
                    console.error('[WS] Erro ao parsear mensagem:', e)
                }
            }

            ws.onerror = (error) => {
                console.error('[WS] Erro:', error)
                onError?.(error)
            }

            ws.onclose = (event) => {
                console.log(`[WS] Desconectado (${event.code})`)
                setIsConnected(false)
                onDisconnected?.()

                // Tentar reconectar se não foi fechamento intencional
                if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
                    reconnectAttempts.current++
                    console.log(`[WS] Tentando reconectar (${reconnectAttempts.current}/${maxReconnectAttempts})...`)

                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect()
                    }, reconnectDelay)
                }
            }

            wsRef.current = ws
        } catch (error) {
            console.error('[WS] Erro ao criar conexão:', error)
        }
    }, [projectId, enabled, onStatusUpdate, onConnected, onDisconnected, onError])

    // Conectar automaticamente quando habilitado
    useEffect(() => {
        connect()

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
            }
            if (wsRef.current) {
                wsRef.current.close(1000) // Fechamento intencional
            }
        }
    }, [connect])

    // Enviar mensagem
    const send = useCallback((message: object) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message))
        }
    }, [])

    // Reconectar manualmente
    const reconnect = useCallback(() => {
        reconnectAttempts.current = 0
        connect()
    }, [connect])

    // Ping para manter conexão viva
    useEffect(() => {
        if (!isConnected) return

        const pingInterval = setInterval(() => {
            send({ type: 'ping' })
        }, 30000) // Ping a cada 30s

        return () => clearInterval(pingInterval)
    }, [isConnected, send])

    return {
        isConnected,
        lastStatus,
        send,
        reconnect,
    }
}

export default useProjectWebSocket
