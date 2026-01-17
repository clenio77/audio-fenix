/**
 * Upload Page - Frontend
 * 
 * Página inicial onde o usuário faz upload do arquivo de áudio.
 */
import { useState } from 'react'
import { Upload, FileAudio, AlertCircle } from 'lucide-react'
import { apiService } from '@/services/api'

interface UploadPageProps {
    onProjectCreated: (projectId: string) => void
}

export default function UploadPage({ onProjectCreated }: UploadPageProps) {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [dragActive, setDragActive] = useState(false)

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0])
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault()
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0])
        }
    }

    const handleFile = (file: File) => {
        // Validar extensão do arquivo
        const validExtensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        const fileName = file.name.toLowerCase()
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext))

        if (!hasValidExtension) {
            setError('Formato não suportado. Use: .mp3, .wav, .flac, .ogg, .m4a')
            return
        }

        // Validar tamanho (20MB para demo)
        const maxSize = 20 * 1024 * 1024
        if (file.size > maxSize) {
            setError('Arquivo muito grande. Limite: 20MB')
            return
        }

        setFile(file)
        setError(null)
    }

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        setError(null)

        try {
            const response = await apiService.uploadAudio(file)
            onProjectCreated(response.project_id)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erro ao fazer upload')
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="max-w-2xl mx-auto">
            {/* Hero Section */}
            <div className="text-center mb-12">
                <h2 className="text-4xl font-bold mb-4 text-glow">
                    Separe sua música em faixas individuais
                </h2>
                <p className="text-gray-400 text-lg">
                    Faça upload de um arquivo de áudio e nossa IA vai separar em Vocal, Bateria, Baixo e Outros
                </p>
            </div>

            {/* Upload Area */}
            <div
                className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center
          transition-all duration-300
          ${dragActive ? 'border-mixer-accent bg-mixer-accent/10' : 'border-gray-600 hover:border-gray-500'}
          ${file ? 'bg-mixer-panel' : ''}
        `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept="audio/*"
                    onChange={handleChange}
                    disabled={uploading}
                />

                {!file ? (
                    <>
                        <Upload className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                        <p className="text-xl mb-2">Arraste um arquivo de áudio aqui</p>
                        <p className="text-gray-500 mb-6">ou</p>
                        <label
                            htmlFor="file-upload"
                            className="inline-block px-6 py-3 bg-mixer-accent text-black font-semibold rounded-lg cursor-pointer hover:bg-mixer-accent/90 transition-colors"
                        >
                            Escolher Arquivo
                        </label>
                        <p className="text-sm text-gray-500 mt-4">
                            Formatos suportados: MP3, WAV, FLAC, OGG, M4A (máx. 20MB)
                        </p>
                    </>
                ) : (
                    <>
                        <FileAudio className="w-16 h-16 mx-auto mb-4 text-mixer-accent" />
                        <p className="text-xl mb-2 font-semibold">{file.name}</p>
                        <p className="text-gray-400 mb-6">
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                        <div className="flex gap-4 justify-center">
                            <button
                                onClick={() => setFile(null)}
                                className="px-6 py-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                                disabled={uploading}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="px-6 py-3 bg-mixer-accent text-black font-semibold rounded-lg hover:bg-mixer-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {uploading ? 'Enviando...' : 'Processar Áudio'}
                            </button>
                        </div>
                    </>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="mt-6 p-4 bg-red-500/10 border border-red-500 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="font-semibold text-red-500">Erro</p>
                        <p className="text-sm text-red-400">{error}</p>
                    </div>
                </div>
            )}

            {/* Features */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 glass rounded-xl">
                    <div className="text-3xl mb-3">🎤</div>
                    <h3 className="font-semibold mb-2">Isolar Vocal</h3>
                    <p className="text-sm text-gray-400">Extraia a voz principal da música</p>
                </div>
                <div className="text-center p-6 glass rounded-xl">
                    <div className="text-3xl mb-3">🥁</div>
                    <h3 className="font-semibold mb-2">Remover Bateria</h3>
                    <p className="text-sm text-gray-400">Crie versões drumless para praticar</p>
                </div>
                <div className="text-center p-6 glass rounded-xl">
                    <div className="text-3xl mb-3">🎚️</div>
                    <h3 className="font-semibold mb-2">Mixer Profissional</h3>
                    <p className="text-sm text-gray-400">Controle total sobre cada faixa</p>
                </div>
            </div>
        </div>
    )
}
