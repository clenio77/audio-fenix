/**
 * Auth Service - Frontend
 * 
 * Serviço para autenticação com a API.
 */
import axios from 'axios'
import { useAuthStore, User } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const authApi = axios.create({
    baseURL: `${API_URL}/api/auth`,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Interceptor para adicionar token de autenticação
authApi.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Interceptor para refresh automático de token
authApi.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            const refreshToken = useAuthStore.getState().refreshToken
            if (refreshToken) {
                try {
                    const response = await authApi.post('/refresh', {
                        refresh_token: refreshToken,
                    })

                    const { access_token, refresh_token: newRefreshToken, user } = response.data
                    useAuthStore.getState().login(user, access_token, newRefreshToken)

                    originalRequest.headers.Authorization = `Bearer ${access_token}`
                    return authApi(originalRequest)
                } catch (refreshError) {
                    useAuthStore.getState().logout()
                    return Promise.reject(refreshError)
                }
            }
        }

        return Promise.reject(error)
    }
)

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    name?: string
}

export interface AuthResponse {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: User
}

export const authService = {
    /**
     * Registra um novo usuário
     */
    async register(data: RegisterRequest): Promise<AuthResponse> {
        const response = await authApi.post<AuthResponse>('/register', data)

        // Salvar no store
        useAuthStore.getState().login(
            response.data.user,
            response.data.access_token,
            response.data.refresh_token
        )

        return response.data
    },

    /**
     * Faz login de um usuário
     */
    async login(data: LoginRequest): Promise<AuthResponse> {
        const response = await authApi.post<AuthResponse>('/login', data)

        // Salvar no store
        useAuthStore.getState().login(
            response.data.user,
            response.data.access_token,
            response.data.refresh_token
        )

        return response.data
    },

    /**
     * Renova o token de acesso
     */
    async refreshToken(): Promise<AuthResponse> {
        const refreshToken = useAuthStore.getState().refreshToken

        if (!refreshToken) {
            throw new Error('No refresh token available')
        }

        const response = await authApi.post<AuthResponse>('/refresh', {
            refresh_token: refreshToken,
        })

        useAuthStore.getState().login(
            response.data.user,
            response.data.access_token,
            response.data.refresh_token
        )

        return response.data
    },

    /**
     * Busca dados do usuário atual
     */
    async getMe(): Promise<User> {
        const response = await authApi.get<User>('/me')
        useAuthStore.getState().updateUser(response.data)
        return response.data
    },

    /**
     * Faz logout do usuário
     */
    async logout(): Promise<void> {
        try {
            await authApi.post('/logout')
        } finally {
            useAuthStore.getState().logout()
        }
    },

    /**
     * Altera a senha do usuário
     */
    async changePassword(currentPassword: string, newPassword: string): Promise<void> {
        await authApi.post('/change-password', {
            current_password: currentPassword,
            new_password: newPassword,
        })
    },
}
