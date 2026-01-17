/**
 * TypeScript Types - Frontend
 */

export enum ProjectStatus {
    PENDING = 'pending',
    PROCESSING = 'processing',
    READY = 'ready',
    FAILED = 'failed',
}

export enum StemType {
    VOCALS = 'vocals',
    DRUMS = 'drums',
    BASS = 'bass',
    OTHER = 'other',
    CLICK = 'click',
    MIDI = 'midi',
    SCORE = 'score',
}

export interface StemInfo {
    type: StemType
    url: string
    size_mb?: number
}

export interface Project {
    project_id: string
    status: ProjectStatus
    progress: number
    message?: string
    error?: string
    stems?: StemInfo[]
    created_at: string
}

export interface UploadResponse {
    project_id: string
    status: ProjectStatus
    message: string
}

export interface ExportRequest {
    project_id: string
    volumes: Record<StemType, number>
    mutes: Record<StemType, boolean>
    format: 'mp3' | 'wav'
}

export interface ExportResponse {
    download_url: string
    expires_at: string
}

export interface ChannelState {
    volume: number
    muted: boolean
    solo: boolean
    pan: number
}

export type MixerState = Record<StemType, ChannelState>

export interface ChordInfo {
    time: number
    chord: string
    confidence: number
    duration: number
}
