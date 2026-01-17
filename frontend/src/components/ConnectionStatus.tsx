/**
 * ConnectionStatus Component - Frontend
 * 
 * Indicador visual de status de conexão WebSocket.
 */
import { Wifi, WifiOff, RefreshCw } from 'lucide-react'

interface ConnectionStatusProps {
    isConnected: boolean
    onReconnect?: () => void
    showLabel?: boolean
}

export default function ConnectionStatus({
    isConnected,
    onReconnect,
    showLabel = true,
}: ConnectionStatusProps) {
    return (
        <div className="flex items-center gap-2">
            {isConnected ? (
                <>
                    <div className="relative">
                        <Wifi className="w-4 h-4 text-green-400" />
                        <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    </div>
                    {showLabel && (
                        <span className="text-xs text-green-400">Tempo real</span>
                    )}
                </>
            ) : (
                <>
                    <WifiOff className="w-4 h-4 text-gray-500" />
                    {showLabel && (
                        <span className="text-xs text-gray-500">Desconectado</span>
                    )}
                    {onReconnect && (
                        <button
                            onClick={onReconnect}
                            className="p-1 rounded hover:bg-gray-700/50 transition-all"
                            title="Reconectar"
                        >
                            <RefreshCw className="w-3 h-3 text-gray-400 hover:text-white" />
                        </button>
                    )}
                </>
            )}
        </div>
    )
}
