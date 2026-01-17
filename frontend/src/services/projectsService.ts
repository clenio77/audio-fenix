/**
 * Projects Service - Frontend
 * 
 * Serviço para gerenciamento de projetos do usuário.
 */
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const projectsApi = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Interceptor para adicionar token de autenticação
projectsApi.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})


// ===============================
// Types
// ===============================

export interface ProjectListItem {
    id: string
    original_filename: string
    status: 'pending' | 'processing' | 'ready' | 'failed'
    progress: number
    created_at: string
    duration_seconds: number | null
    file_size_mb: number
}

export interface ProjectDetail {
    id: string
    original_filename: string
    status: 'pending' | 'processing' | 'ready' | 'failed'
    progress: number
    message: string
    error: string | null
    created_at: string
    updated_at: string
    expires_at: string | null
    duration_seconds: number | null
    file_size_mb: number
    ai_model: string | null
    stems: Array<{
        id: string
        type: string
        url: string
    }>
}

export interface ProjectListResponse {
    projects: ProjectListItem[]
    total: number
    page: number
    page_size: number
    has_more: boolean
}

export interface ProjectStats {
    total: number
    ready: number
    processing: number
    failed: number
    pending: number
}


// ===============================
// Service
// ===============================

export const projectsService = {
    /**
     * Lista projetos do usuário com paginação
     */
    async listProjects(
        page: number = 1,
        pageSize: number = 10,
        statusFilter?: string
    ): Promise<ProjectListResponse> {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString(),
        })

        if (statusFilter) {
            params.append('status_filter', statusFilter)
        }

        const response = await projectsApi.get<ProjectListResponse>(
            `/projects?${params.toString()}`
        )
        return response.data
    },

    /**
     * Busca detalhes de um projeto específico
     */
    async getProject(projectId: string): Promise<ProjectDetail> {
        const response = await projectsApi.get<ProjectDetail>(`/projects/${projectId}`)
        return response.data
    },

    /**
     * Exclui um projeto
     */
    async deleteProject(projectId: string): Promise<void> {
        await projectsApi.delete(`/projects/${projectId}`)
    },

    /**
     * Retorna estatísticas dos projetos
     */
    async getStats(): Promise<ProjectStats> {
        const response = await projectsApi.get<ProjectStats>('/projects/stats/summary')
        return response.data
    },
}

export default projectsService
