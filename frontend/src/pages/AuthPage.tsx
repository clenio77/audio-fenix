/**
 * Login Page - Frontend
 * 
 * Página de login do IsoMix Studio.
 */
import { useState } from 'react'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/store/authStore'
import { Mail, Lock, LogIn, UserPlus, Loader2, Music } from 'lucide-react'

interface AuthPageProps {
    onSuccess?: () => void
}

export default function AuthPage({ onSuccess }: AuthPageProps) {
    const [isLogin, setIsLogin] = useState(true)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [name, setName] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    const { isAuthenticated } = useAuthStore()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setIsLoading(true)

        try {
            if (isLogin) {
                await authService.login({ email, password })
            } else {
                if (password !== confirmPassword) {
                    setError('As senhas não coincidem')
                    setIsLoading(false)
                    return
                }
                await authService.register({ email, password, name: name || undefined })
            }

            if (onSuccess) {
                onSuccess()
            }
        } catch (err: any) {
            const message = err.response?.data?.detail || 'Erro ao processar solicitação'
            setError(message)
        } finally {
            setIsLoading(false)
        }
    }

    if (isAuthenticated) {
        return null // Será redirecionado pelo componente pai
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 flex items-center justify-center p-6">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-4 shadow-lg shadow-purple-500/30">
                        <Music className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">IsoMix Studio</h1>
                    <p className="text-gray-400">Separação de áudio com IA</p>
                </div>

                {/* Card */}
                <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-8 shadow-2xl">
                    {/* Tabs */}
                    <div className="flex bg-gray-900/50 rounded-xl p-1 mb-6">
                        <button
                            onClick={() => { setIsLogin(true); setError(null) }}
                            className={`flex-1 py-2.5 px-4 rounded-lg font-medium transition-all duration-200 ${isLogin
                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                                    : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <LogIn className="w-4 h-4 inline-block mr-2" />
                            Entrar
                        </button>
                        <button
                            onClick={() => { setIsLogin(false); setError(null) }}
                            className={`flex-1 py-2.5 px-4 rounded-lg font-medium transition-all duration-200 ${!isLogin
                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                                    : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <UserPlus className="w-4 h-4 inline-block mr-2" />
                            Criar conta
                        </button>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Name (only for register) */}
                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Nome
                                </label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="Seu nome"
                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 pl-11 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                    />
                                    <UserPlus className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                </div>
                            </div>
                        )}

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="seu@email.com"
                                    required
                                    className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 pl-11 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                />
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Senha
                            </label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    minLength={6}
                                    className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 pl-11 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                />
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            </div>
                        </div>

                        {/* Confirm Password (only for register) */}
                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Confirmar senha
                                </label>
                                <div className="relative">
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="••••••••"
                                        required
                                        minLength={6}
                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 pl-11 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                    />
                                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                </div>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processando...
                                </>
                            ) : isLogin ? (
                                <>
                                    <LogIn className="w-5 h-5" />
                                    Entrar
                                </>
                            ) : (
                                <>
                                    <UserPlus className="w-5 h-5" />
                                    Criar conta
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-6 text-center text-sm text-gray-500">
                        {isLogin ? (
                            <p>
                                Não tem uma conta?{' '}
                                <button
                                    onClick={() => { setIsLogin(false); setError(null) }}
                                    className="text-purple-400 hover:text-purple-300 font-medium"
                                >
                                    Crie agora
                                </button>
                            </p>
                        ) : (
                            <p>
                                Já tem uma conta?{' '}
                                <button
                                    onClick={() => { setIsLogin(true); setError(null) }}
                                    className="text-purple-400 hover:text-purple-300 font-medium"
                                >
                                    Faça login
                                </button>
                            </p>
                        )}
                    </div>
                </div>

                {/* Plan Info */}
                <div className="mt-6 text-center text-sm text-gray-500">
                    <p>Comece gratuitamente • Sem cartão de crédito</p>
                    <p className="mt-1">5 uploads/dia • Arquivos até 20MB</p>
                </div>
            </div>
        </div>
    )
}
