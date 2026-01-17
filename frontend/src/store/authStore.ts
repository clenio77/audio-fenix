/**
 * Auth Context - Frontend
 * 
 * Contexto para gerenciar estado de autenticação.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
    id: string
    email: string
    name: string | null
    plan: 'free' | 'pro'
    is_verified: boolean
    created_at: string
}

export interface AuthState {
    // State
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    login: (user: User, accessToken: string, refreshToken: string) => void
    logout: () => void
    updateUser: (user: Partial<User>) => void
    setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            // Initial state
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,

            // Actions
            login: (user, accessToken, refreshToken) => set({
                user,
                accessToken,
                refreshToken,
                isAuthenticated: true,
                isLoading: false,
            }),

            logout: () => set({
                user: null,
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
                isLoading: false,
            }),

            updateUser: (userData) => set((state) => ({
                user: state.user ? { ...state.user, ...userData } : null,
            })),

            setLoading: (loading) => set({ isLoading: loading }),
        }),
        {
            name: 'isomix-auth',
            partialize: (state) => ({
                user: state.user,
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
)
