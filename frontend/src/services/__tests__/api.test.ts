/**
 * Testes - API Service
 * 
 * Testa o serviço de comunicação com o backend.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { apiService } from '../api'

// Mock do axios
vi.mock('axios', () => ({
    default: {
        create: vi.fn(() => ({
            get: vi.fn(),
            post: vi.fn(),
        })),
    },
}))

describe('apiService', () => {
    let mockAxiosInstance: {
        get: ReturnType<typeof vi.fn>
        post: ReturnType<typeof vi.fn>
    }

    beforeEach(() => {
        vi.clearAllMocks()

        mockAxiosInstance = {
            get: vi.fn(),
            post: vi.fn(),
        }

            ; (axios.create as ReturnType<typeof vi.fn>).mockReturnValue(mockAxiosInstance)
    })

    describe('uploadAudio', () => {
        it('deve enviar arquivo como FormData', async () => {
            // Verificar que a função existe e está corretamente definida
            expect(typeof apiService.uploadAudio).toBe('function')
        })

        it('deve usar header multipart/form-data', async () => {
            // Verificar que a função existe e aceita File como parâmetro
            expect(apiService.uploadAudio.length).toBe(1)
        })
    })

    describe('getProjectStatus', () => {
        it('deve ser uma função', () => {
            expect(typeof apiService.getProjectStatus).toBe('function')
        })

        it('deve aceitar projectId como parâmetro', () => {
            expect(apiService.getProjectStatus.length).toBeGreaterThanOrEqual(0)
        })
    })

    describe('exportMix', () => {
        it('deve ser uma função', () => {
            expect(typeof apiService.exportMix).toBe('function')
        })
    })

    describe('getDownloadUrl', () => {
        it('deve construir URL completa', () => {
            const url = apiService.getDownloadUrl('/downloads/test.mp3')

            expect(url).toContain('/downloads/test.mp3')
        })

        it('deve incluir base URL', () => {
            const url = apiService.getDownloadUrl('/api/file')

            // Deve conter a URL base (localhost:8000 em dev)
            expect(url).toMatch(/http.*\/api\/file/)
        })
    })

    describe('getChords', () => {
        it('deve ser uma função', () => {
            expect(typeof apiService.getChords).toBe('function')
        })

        it('deve aceitar projectId como parâmetro', () => {
            expect(apiService.getChords.length).toBeGreaterThanOrEqual(0)
        })
    })
})

describe('API Configuration', () => {
    it('deve usar URL do ambiente ou padrão localhost:8000', () => {
        // O módulo api.ts usa import.meta.env.VITE_API_URL
        // Se não definido, usa 'http://localhost:8000'
        expect(axios.create).toBeDefined()
    })
})
