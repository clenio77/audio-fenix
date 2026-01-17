/**
 * Projects Page - Frontend
 * 
 * Página de histórico de projetos do usuário.
 */
import { useState, useEffect } from 'react'
import {
    Music, Clock, Trash2, Play, Loader2, RefreshCw,
    FileAudio, CheckCircle, XCircle, AlertTriangle, ArrowLeft
} from 'lucide-react'
import { projectsService, type ProjectListItem, type ProjectStats } from '@/services/projectsService'

interface ProjectsPageProps {
    onOpenProject: (projectId: string) => void
    onBack: () => void
}

export default function ProjectsPage({ onOpenProject, onBack }: ProjectsPageProps) {
    const [projects, setProjects] = useState<ProjectListItem[]>([])
    const [stats, setStats] = useState<ProjectStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(false)
    const [total, setTotal] = useState(0)
    const [statusFilter, setStatusFilter] = useState<string>('')
    const [deleting, setDeleting] = useState<string | null>(null)

    // Carregar projetos
    const loadProjects = async (pageNum: number = 1, append: boolean = false) => {
        try {
            setLoading(true)
            const response = await projectsService.listProjects(
                pageNum,
                10,
                statusFilter || undefined
            )

            if (append) {
                setProjects(prev => [...prev, ...response.projects])
            } else {
                setProjects(response.projects)
            }

            setTotal(response.total)
            setHasMore(response.has_more)
            setPage(pageNum)
        } catch (error) {
            console.error('Erro ao carregar projetos:', error)
        } finally {
            setLoading(false)
        }
    }

    // Carregar estatísticas
    const loadStats = async () => {
        try {
            const data = await projectsService.getStats()
            setStats(data)
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error)
        }
    }

    // Carregar ao montar e quando filtro mudar
    useEffect(() => {
        loadProjects(1, false)
        loadStats()
    }, [statusFilter])

    // Excluir projeto
    const handleDelete = async (projectId: string) => {
        if (!confirm('Tem certeza que deseja excluir este projeto?')) return

        try {
            setDeleting(projectId)
            await projectsService.deleteProject(projectId)
            setProjects(prev => prev.filter(p => p.id !== projectId))
            setTotal(prev => prev - 1)
            loadStats()
        } catch (error) {
            console.error('Erro ao excluir projeto:', error)
            alert('Erro ao excluir projeto')
        } finally {
            setDeleting(null)
        }
    }

    // Formatadores
    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        })
    }

    const formatDuration = (seconds: number | null) => {
        if (!seconds) return '--:--'
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const formatSize = (mb: number) => {
        if (mb < 1) return `${Math.round(mb * 1000)} KB`
        return `${mb.toFixed(1)} MB`
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'ready':
                return (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                        <CheckCircle className="w-3 h-3" />
                        Pronto
                    </span>
                )
            case 'processing':
                return (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Processando
                    </span>
                )
            case 'failed':
                return (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30">
                        <XCircle className="w-3 h-3" />
                        Erro
                    </span>
                )
            default:
                return (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                        <AlertTriangle className="w-3 h-3" />
                        Pendente
                    </span>
                )
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black">
            {/* Header */}
            <div className="px-8 py-6 border-b border-gray-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={onBack}
                            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                                <Music className="w-7 h-7 text-purple-400" />
                                Meus Projetos
                            </h1>
                            <p className="text-gray-400 text-sm mt-1">
                                {total} projeto{total !== 1 ? 's' : ''} no total
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => loadProjects(1, false)}
                        disabled={loading}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg transition-all disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        Atualizar
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="px-8 py-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-green-500/20">
                            <div className="text-3xl font-bold text-green-400">{stats.ready}</div>
                            <div className="text-sm text-gray-400">Prontos</div>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-blue-500/20">
                            <div className="text-3xl font-bold text-blue-400">{stats.processing}</div>
                            <div className="text-sm text-gray-400">Processando</div>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-yellow-500/20">
                            <div className="text-3xl font-bold text-yellow-400">{stats.pending}</div>
                            <div className="text-sm text-gray-400">Pendentes</div>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-red-500/20">
                            <div className="text-3xl font-bold text-red-400">{stats.failed}</div>
                            <div className="text-sm text-gray-400">Falhas</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="px-8 pb-4">
                <div className="flex gap-2">
                    {['', 'ready', 'processing', 'pending', 'failed'].map((filter) => (
                        <button
                            key={filter}
                            onClick={() => setStatusFilter(filter)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${statusFilter === filter
                                    ? 'bg-purple-500 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                                }`}
                        >
                            {filter === '' ? 'Todos' :
                                filter === 'ready' ? 'Prontos' :
                                    filter === 'processing' ? 'Processando' :
                                        filter === 'pending' ? 'Pendentes' : 'Falhas'}
                        </button>
                    ))}
                </div>
            </div>

            {/* Project List */}
            <div className="px-8 pb-8">
                {loading && projects.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 className="w-12 h-12 text-purple-400 animate-spin" />
                        <p className="mt-4 text-gray-400">Carregando projetos...</p>
                    </div>
                ) : projects.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 bg-gray-800/30 rounded-2xl border border-gray-700/50">
                        <FileAudio className="w-16 h-16 text-gray-600" />
                        <p className="mt-4 text-gray-400 text-lg">Nenhum projeto encontrado</p>
                        <p className="text-gray-500 text-sm">Faça upload de um áudio para começar</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {projects.map((project) => (
                            <div
                                key={project.id}
                                className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-gray-700/50 hover:border-purple-500/30 transition-all group"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4 flex-1">
                                        {/* Icon */}
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center border border-purple-500/30">
                                            <FileAudio className="w-6 h-6 text-purple-400" />
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-medium text-white truncate">
                                                {project.original_filename}
                                            </h3>
                                            <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                                                <span className="flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {formatDuration(project.duration_seconds)}
                                                </span>
                                                <span>{formatSize(project.file_size_mb)}</span>
                                                <span>{formatDate(project.created_at)}</span>
                                            </div>
                                        </div>

                                        {/* Status */}
                                        <div className="hidden md:block">
                                            {getStatusBadge(project.status)}
                                        </div>

                                        {/* Progress bar for processing */}
                                        {project.status === 'processing' && (
                                            <div className="hidden md:block w-32">
                                                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                                                        style={{ width: `${project.progress}%` }}
                                                    />
                                                </div>
                                                <p className="text-xs text-center text-gray-400 mt-1">
                                                    {project.progress}%
                                                </p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Actions */}
                                    <div className="flex items-center gap-2 ml-4">
                                        {project.status === 'ready' && (
                                            <button
                                                onClick={() => onOpenProject(project.id)}
                                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-400 hover:to-pink-400 transition-all"
                                            >
                                                <Play className="w-4 h-4" />
                                                Abrir
                                            </button>
                                        )}

                                        <button
                                            onClick={() => handleDelete(project.id)}
                                            disabled={deleting === project.id}
                                            className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all disabled:opacity-50"
                                            title="Excluir projeto"
                                        >
                                            {deleting === project.id ? (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <Trash2 className="w-4 h-4" />
                                            )}
                                        </button>
                                    </div>
                                </div>

                                {/* Mobile status */}
                                <div className="md:hidden mt-3 flex items-center justify-between">
                                    {getStatusBadge(project.status)}
                                    {project.status === 'processing' && (
                                        <span className="text-xs text-gray-400">{project.progress}%</span>
                                    )}
                                </div>
                            </div>
                        ))}

                        {/* Load More */}
                        {hasMore && (
                            <div className="flex justify-center pt-4">
                                <button
                                    onClick={() => loadProjects(page + 1, true)}
                                    disabled={loading}
                                    className="px-6 py-3 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg transition-all disabled:opacity-50"
                                >
                                    {loading ? (
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    ) : (
                                        'Carregar mais'
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
