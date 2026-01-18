import { useRef, useEffect, useState } from 'react';
import { ChordInfo } from '@/types';
import { FileText, Music, LayoutList, MonitorPlay } from 'lucide-react';

interface LyricSegment {
    start: number;
    end: number;
    text: string;
}

interface SongBookProps {
    lyrics: LyricSegment[];
    chords: ChordInfo[];
    currentTime: number;
}

export default function SongBook({ lyrics, chords, currentTime }: SongBookProps) {
    const activeRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [focusMode, setFocusMode] = useState(false);

    // Função para pegar os acordes de um intervalo de tempo
    const getChordsForInterval = (start: number, end: number) => {
        return chords.filter(c => c.time >= start && c.time < end);
    };

    // Encontrar o índice da frase atual
    const activeIndex = lyrics.findIndex(s => currentTime >= s.start - 0.2 && currentTime <= s.end);

    // Scroll automático
    useEffect(() => {
        if (activeRef.current && containerRef.current && !focusMode) {
            activeRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'nearest'
            });
        }
    }, [currentTime, focusMode]);

    // Filtrar letras se estiver no modo foco
    const visibleLyrics = focusMode && activeIndex !== -1
        ? lyrics.slice(Math.max(0, activeIndex - 1), activeIndex + 2)
        : lyrics;

    return (
        <div className="w-full bg-slate-900/80 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-2xl transition-all duration-500">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-indigo-500/20 rounded-2xl border border-indigo-500/30">
                        <FileText className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white leading-none">Songbook IA</h3>
                        <p className="text-xs text-indigo-400/60 mt-1 uppercase tracking-widest font-bold">Cifra + Letra Sincronizada</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setFocusMode(!focusMode)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all border ${focusMode ? 'bg-indigo-500 text-white border-indigo-400' : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10'}`}
                    >
                        {focusMode ? <LayoutList className="w-4 h-4" /> : <MonitorPlay className="w-4 h-4" />}
                        {focusMode ? 'Ver Tudo' : 'Modo Foco'}
                    </button>

                    <div className="hidden sm:flex gap-2">
                        <span className="text-[10px] bg-white/5 px-3 py-1 rounded-full border border-white/10 text-gray-400 font-mono">
                            {detectedLanguage(lyrics)}
                        </span>
                    </div>
                </div>
            </div>

            <div
                ref={containerRef}
                className={`space-y-4 overflow-y-auto pr-4 custom-scrollbar scroll-smooth transition-all duration-500 ${focusMode ? 'max-h-[350px]' : 'max-h-[600px]'}`}
            >
                {lyrics.length > 0 ? (
                    visibleLyrics.map((segment, index) => {
                        const originalIndex = lyrics.indexOf(segment);
                        const isActive = currentTime >= segment.start - 0.2 && currentTime <= segment.end;
                        const segmentChords = getChordsForInterval(segment.start, segment.end);

                        return (
                            <div
                                key={originalIndex}
                                ref={isActive ? activeRef : null}
                                className={`transition-all duration-700 rounded-2xl p-6 border ${isActive
                                    ? 'bg-indigo-500/20 border-indigo-500/50 shadow-lg shadow-indigo-500/10 scale-[1.02] opacity-100'
                                    : focusMode ? 'opacity-40 scale-95 border-transparent' : 'opacity-30 grayscale-[0.5] hover:opacity-100 hover:grayscale-0 border-transparent'
                                    }`}
                            >
                                {/* Acordes deste segmento */}
                                <div className="flex flex-wrap gap-6 mb-3">
                                    {segmentChords.map((c, i) => (
                                        <span
                                            key={i}
                                            className={`font-mono font-black text-2xl tracking-tighter transition-colors duration-500 ${isActive ? 'text-amber-400 animate-pulse' : 'text-indigo-300'}`}
                                        >
                                            {c.chord}
                                        </span>
                                    ))}
                                    {segmentChords.length === 0 && isActive && (
                                        <span className="text-xs text-gray-500 italic flex items-center gap-1">
                                            <Music className="w-3 h-3" /> (Execução instrumental)
                                        </span>
                                    )}
                                </div>

                                {/* Texto da letra */}
                                <p className={`text-2xl font-bold tracking-tight transition-all duration-500 ${isActive ? 'text-white translate-x-1' : 'text-gray-500'}`}>
                                    {segment.text}
                                </p>

                                {/* Marcador de tempo */}
                                <div className="flex items-center gap-2 mt-3">
                                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${isActive ? 'bg-indigo-500 text-white' : 'text-gray-600 bg-white/5'}`}>
                                        {Math.floor(segment.start / 60)}:{(segment.start % 60).toFixed(0).padStart(2, '0')}
                                    </span>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div className="text-center py-20 bg-black/20 rounded-3xl border border-dashed border-white/10">
                        <Music className="w-12 h-12 text-gray-600 mx-auto mb-4 opacity-20" />
                        <p className="text-gray-500 italic">Processando letras...</p>
                    </div>
                )}
            </div>

            {!focusMode && (
                <div className="mt-8 pt-6 border-t border-white/5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-amber-500/5 p-4 rounded-2xl border border-amber-500/10">
                        <h4 className="text-amber-400 text-xs font-bold uppercase mb-1">Dica de Estudo</h4>
                        <p className="text-gray-400 text-[11px] leading-relaxed">As frases brilham quando devem ser cantadas. Use o "Modo Foco" para esconder o que já passou.</p>
                    </div>
                    <div className="bg-indigo-500/5 p-4 rounded-2xl border border-indigo-500/10">
                        <h4 className="text-indigo-400 text-xs font-bold uppercase mb-1">Sincronização</h4>
                        <p className="text-gray-400 text-[11px] leading-relaxed">Letras e acordes são extraídos via IA. O Player está fixo na base da tela para facilitar o controle.</p>
                    </div>
                </div>
            )}
        </div>
    );
}

function detectedLanguage(lyrics: LyricSegment[]) {
    if (!lyrics.length) return "WHISPER AI";
    return "AUTO-DETECÇÃO ATIVA";
}
