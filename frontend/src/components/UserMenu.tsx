/**
 * User Menu Component - Frontend
 * 
 * Menu dropdown com informações do usuário e ações.
 */
import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'
import { User, LogOut, Settings, Crown, ChevronDown } from 'lucide-react'

interface UserMenuProps {
    onLogout?: () => void
}

export default function UserMenu({ onLogout }: UserMenuProps) {
    const [isOpen, setIsOpen] = useState(false)
    const menuRef = useRef<HTMLDivElement>(null)
    const { user, logout } = useAuthStore()

    // Fechar menu ao clicar fora
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleLogout = async () => {
        try {
            await authService.logout()
        } finally {
            logout()
            if (onLogout) onLogout()
        }
    }

    if (!user) return null

    const isPro = user.plan === 'pro'

    return (
        <div className="relative" ref={menuRef}>
            {/* Trigger */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700/50 rounded-xl px-4 py-2.5 transition-all"
            >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isPro
                        ? 'bg-gradient-to-br from-amber-500 to-orange-500'
                        : 'bg-gradient-to-br from-purple-500 to-pink-500'
                    }`}>
                    {isPro ? (
                        <Crown className="w-4 h-4 text-white" />
                    ) : (
                        <User className="w-4 h-4 text-white" />
                    )}
                </div>

                {/* Name */}
                <div className="text-left hidden sm:block">
                    <div className="text-sm font-medium text-white">
                        {user.name || user.email.split('@')[0]}
                    </div>
                    <div className="text-xs text-gray-400 flex items-center gap-1">
                        {isPro ? (
                            <>
                                <Crown className="w-3 h-3 text-amber-400" />
                                Pro
                            </>
                        ) : (
                            'Free'
                        )}
                    </div>
                </div>

                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50">
                    {/* User Info */}
                    <div className="px-4 py-3 bg-gray-900/50 border-b border-gray-700">
                        <div className="font-medium text-white">{user.name || 'Usuário'}</div>
                        <div className="text-sm text-gray-400">{user.email}</div>
                    </div>

                    {/* Plan Badge */}
                    {!isPro && (
                        <div className="px-4 py-3 border-b border-gray-700">
                            <button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all">
                                <Crown className="w-4 h-4" />
                                Upgrade para Pro
                            </button>
                        </div>
                    )}

                    {/* Menu Items */}
                    <div className="py-2">
                        <button
                            onClick={() => setIsOpen(false)}
                            className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-gray-700/50 transition-all"
                        >
                            <Settings className="w-4 h-4" />
                            Configurações
                        </button>

                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all"
                        >
                            <LogOut className="w-4 h-4" />
                            Sair
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
