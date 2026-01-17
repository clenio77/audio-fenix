import { useState } from 'react'
import { Music, History } from 'lucide-react'
import UploadPage from './pages/UploadPage'
import MixerPage from './pages/MixerPage'
import ProjectsPage from './pages/ProjectsPage'
import AuthPage from './pages/AuthPage'
import UserMenu from './components/UserMenu'
import { useAuthStore } from './store/authStore'

type View = 'upload' | 'mixer' | 'projects'

function App() {
    const [projectId, setProjectId] = useState<string | null>(null)
    const [view, setView] = useState<View>('upload')
    const { isAuthenticated, user } = useAuthStore()

    // Se não está autenticado, mostrar página de login
    if (!isAuthenticated) {
        return <AuthPage onSuccess={() => { }} />
    }

    // Handler para abrir projeto do histórico
    const handleOpenProject = (id: string) => {
        setProjectId(id)
        setView('mixer')
    }

    // Handler para novo projeto criado
    const handleProjectCreated = (id: string) => {
        setProjectId(id)
        setView('mixer')
    }

    // Handler para voltar ao upload
    const handleBackToUpload = () => {
        setProjectId(null)
        setView('upload')
    }

    return (
        <div className="min-h-screen bg-mixer-bg">
            {/* Header */}
            <header className="border-b border-gray-800 bg-mixer-panel sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <button
                            onClick={handleBackToUpload}
                            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
                        >
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
                                <Music className="w-5 h-5 text-white" />
                            </div>
                            <div className="text-left">
                                <h1 className="text-xl font-bold text-white">
                                    IsoMix Studio
                                </h1>
                                <span className="text-xs text-gray-400">
                                    Audio Source Separation
                                </span>
                            </div>
                        </button>

                        {/* Navigation */}
                        <nav className="flex items-center gap-4">
                            <button
                                onClick={() => setView('projects')}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${view === 'projects'
                                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <History className="w-4 h-4" />
                                <span className="hidden sm:inline">Meus Projetos</span>
                            </button>

                            {/* User Menu */}
                            <UserMenu onLogout={() => {
                                setProjectId(null)
                                setView('upload')
                            }} />
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main>
                {view === 'projects' ? (
                    <ProjectsPage
                        onOpenProject={handleOpenProject}
                        onBack={handleBackToUpload}
                    />
                ) : view === 'mixer' && projectId ? (
                    <MixerPage
                        projectId={projectId}
                        onBack={handleBackToUpload}
                    />
                ) : (
                    <div className="container mx-auto px-4 py-8">
                        <UploadPage onProjectCreated={handleProjectCreated} />
                    </div>
                )}
            </main>

            {/* Footer */}
            {view !== 'mixer' && (
                <footer className="border-t border-gray-800 mt-16">
                    <div className="container mx-auto px-4 py-6 text-center text-gray-500 text-sm">
                        <p>Feito com ❤️ e 🎵 | Powered by Demucs AI</p>
                        {user && (
                            <p className="mt-1 text-xs">
                                Plano: {user.plan === 'pro' ? '✨ Pro' : 'Free'}
                                {user.plan !== 'pro' && ' • 5 uploads/dia'}
                            </p>
                        )}
                    </div>
                </footer>
            )}
        </div>
    )
}

export default App
