/**
 * API Service - Frontend
 * 
 * Cliente HTTP para comunicação com o backend.
 */
import axios from 'axios'
import type { UploadResponse, Project, ExportRequest, ExportResponse, ChordInfo } from '@/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
})

export const apiService = {
    /**
     * Upload de arquivo de áudio
     */
    async uploadAudio(file: File): Promise<UploadResponse> {
        const formData = new FormData()
        formData.append('file', file)

        const { data } = await api.post<UploadResponse>('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })

        return data
    },

    /**
     * Consultar status do projeto
     */
    async getProjectStatus(projectId: string): Promise<Project> {
        const { data } = await api.get<Project>(`/status/${projectId}`)
        return data
    },

    /**
     * Exportar mix customizado
     */
    async exportMix(request: ExportRequest): Promise<ExportResponse> {
        const { data } = await api.post<ExportResponse>('/export', request)
        return data
    },

    /**
     * Download de arquivo
     */
    getDownloadUrl(url: string): string {
        return `${API_URL}${url}`
    },

    /**
     * Buscar acordes detectados
     */
    async getChords(projectId: string): Promise<{ chords: ChordInfo[], count: number }> {
        const { data } = await api.get(`/chords/${projectId}`)
        return data
    },

    /**
     * Buscar letra transcrita
     */
    async getLyrics(projectId: string): Promise<{ lyrics: { start: number, end: number, text: string }[], count: number }> {
        const { data } = await api.get(`/lyrics/${projectId}`)
        return data
    },
}
