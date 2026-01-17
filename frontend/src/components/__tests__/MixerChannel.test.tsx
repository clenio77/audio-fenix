/**
 * Testes - MixerChannel Component
 * 
 * Testa o componente de canal do mixer.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MixerChannel from '../MixerChannel'
import { StemType } from '@/types'

describe('MixerChannel', () => {
    const defaultProps = {
        stemType: StemType.VOCALS,
        volume: 75,
        muted: false,
        solo: false,
        color: 'text-mixer-vocals',
        onVolumeChange: vi.fn(),
        onMuteToggle: vi.fn(),
        onSoloToggle: vi.fn(),
    }

    describe('Renderização', () => {
        it('deve renderizar o label correto para Vocals', () => {
            render(<MixerChannel {...defaultProps} />)

            expect(screen.getByText('Vocal')).toBeInTheDocument()
        })

        it('deve renderizar o label correto para Drums', () => {
            render(<MixerChannel {...defaultProps} stemType={StemType.DRUMS} />)

            expect(screen.getByText('Bateria')).toBeInTheDocument()
        })

        it('deve renderizar o label correto para Bass', () => {
            render(<MixerChannel {...defaultProps} stemType={StemType.BASS} />)

            expect(screen.getByText('Baixo')).toBeInTheDocument()
        })

        it('deve renderizar o label correto para Other', () => {
            render(<MixerChannel {...defaultProps} stemType={StemType.OTHER} />)

            expect(screen.getByText('Outros')).toBeInTheDocument()
        })

        it('deve exibir o ícone correto para cada stem', () => {
            const { rerender } = render(<MixerChannel {...defaultProps} stemType={StemType.VOCALS} />)
            expect(screen.getByText('🎤')).toBeInTheDocument()

            rerender(<MixerChannel {...defaultProps} stemType={StemType.DRUMS} />)
            expect(screen.getByText('🥁')).toBeInTheDocument()

            rerender(<MixerChannel {...defaultProps} stemType={StemType.BASS} />)
            expect(screen.getByText('🎸')).toBeInTheDocument()

            rerender(<MixerChannel {...defaultProps} stemType={StemType.OTHER} />)
            expect(screen.getByText('🎹')).toBeInTheDocument()
        })

        it('deve exibir o valor do volume', () => {
            render(<MixerChannel {...defaultProps} volume={50} />)

            expect(screen.getByText('50%')).toBeInTheDocument()
        })

        it('deve renderizar os botões Mute e Solo', () => {
            render(<MixerChannel {...defaultProps} />)

            expect(screen.getByTitle('Mute')).toBeInTheDocument()
            expect(screen.getByTitle('Solo')).toBeInTheDocument()
        })
    })

    describe('Interações', () => {
        it('deve chamar onMuteToggle ao clicar no botão Mute', () => {
            const onMuteToggle = vi.fn()
            render(<MixerChannel {...defaultProps} onMuteToggle={onMuteToggle} />)

            fireEvent.click(screen.getByTitle('Mute'))

            expect(onMuteToggle).toHaveBeenCalledTimes(1)
        })

        it('deve chamar onSoloToggle ao clicar no botão Solo', () => {
            const onSoloToggle = vi.fn()
            render(<MixerChannel {...defaultProps} onSoloToggle={onSoloToggle} />)

            fireEvent.click(screen.getByTitle('Solo'))

            expect(onSoloToggle).toHaveBeenCalledTimes(1)
        })
    })

    describe('Estados visuais', () => {
        it('botão Mute deve ter classe active quando muted=true', () => {
            render(<MixerChannel {...defaultProps} muted={true} />)

            const muteButton = screen.getByTitle('Mute')
            expect(muteButton).toHaveClass('active')
        })

        it('botão Mute não deve ter classe active quando muted=false', () => {
            render(<MixerChannel {...defaultProps} muted={false} />)

            const muteButton = screen.getByTitle('Mute')
            expect(muteButton).not.toHaveClass('active')
        })

        it('botão Solo deve ter classe active quando solo=true', () => {
            render(<MixerChannel {...defaultProps} solo={true} />)

            const soloButton = screen.getByTitle('Solo')
            expect(soloButton).toHaveClass('active')
        })

        it('botão Solo não deve ter classe active quando solo=false', () => {
            render(<MixerChannel {...defaultProps} solo={false} />)

            const soloButton = screen.getByTitle('Solo')
            expect(soloButton).not.toHaveClass('active')
        })
    })

    describe('Acessibilidade', () => {
        it('slider deve ter aria-label', () => {
            render(<MixerChannel {...defaultProps} />)

            expect(screen.getByRole('slider')).toHaveAttribute('aria-label', 'Volume')
        })

        it('botões devem ter atributo title', () => {
            render(<MixerChannel {...defaultProps} />)

            expect(screen.getByTitle('Mute')).toBeInTheDocument()
            expect(screen.getByTitle('Solo')).toBeInTheDocument()
        })
    })
})
