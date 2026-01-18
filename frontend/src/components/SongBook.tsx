import { ChordInfo } from '@/types';
import { FileText, Music } from 'lucide-react';

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
    // Função para pegar os acordes de um intervalo de tempo
    const getChordsForInterval = (start: number, end: number) => {
        return chords.filter(c => c.time >= start && c.time < end);
    };

    return (
        <div className="w-full bg-slate-900/80 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-2xl">
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

                <div className="hidden sm:flex gap-2">
                    <span className="text-[10px] bg-white/5 px-3 py-1 rounded-full border border-white/10 text-gray-400">WHISPER AI</span>
                    <span className="text-[10px] bg-white/5 px-3 py-1 rounded-full border border-white/10 text-gray-400">CHORD AI</span>
                </div>
            </div>

            <div className="space-y-8 max-h-[600px] overflow-y-auto pr-4 custom-scrollbar">
                {lyrics.length > 0 ? (
                    lyrics.map((segment, index) => {
                        const isActive = currentTime >= segment.start && currentTime <= segment.end;
                        const segmentChords = getChordsForInterval(segment.start, segment.end);

                        return (
                            <div
                                key={index}
                                className={`transition-all duration-500 rounded-2xl p-4 ${isActive ? 'bg-indigo-500/10 border-l-4 border-indigo-500' : 'opacity-60 hover:opacity-100'}`}
                            >
                                {/* Acordes deste segmento */}
                                <div className="flex flex-wrap gap-4 mb-2">
                                    {segmentChords.map((c, i) => (
                                        <span
                                            key={i}
                                            className={`font-mono font-bold text-lg ${isActive ? 'text-amber-400' : 'text-indigo-300'}`}
                                        >
                                            {c.chord}
                                        </span>
                                    ))}
                                </div>

                                {/* Texto da letra */}
                                <p className={`text-xl font-medium tracking-wide ${isActive ? 'text-white' : 'text-gray-400'}`}>
                                    {segment.text}
                                </p>

                                {/* Marcador de tempo */}
                                <span className="text-[10px] text-gray-600 mt-2 block font-mono">
                                    {Math.floor(segment.start / 60)}:{(segment.start % 60).toFixed(0).padStart(2, '0')}
                                </span>
                            </div>
                        );
                    })
                ) : (
                    <div className="text-center py-20 bg-black/20 rounded-3xl border border-dashed border-white/10">
                        <Music className="w-12 h-12 text-gray-600 mx-auto mb-4 opacity-20" />
                        <p className="text-gray-500 italic">Transcrição de letra não disponível para este projeto ou ainda processando...</p>
                    </div>
                )}
            </div>

            <div className="mt-8 pt-6 border-t border-white/5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-amber-500/5 p-4 rounded-2xl border border-amber-500/10">
                    <h4 className="text-amber-400 text-xs font-bold uppercase mb-1">Dica de Estudo</h4>
                    <p className="text-gray-400 text-[11px] leading-relaxed">Os acordes destacados acima de cada frase representam as mudanças harmônicas que acontecem durante aquele trecho da letra.</p>
                </div>
                <div className="bg-indigo-500/5 p-4 rounded-2xl border border-indigo-500/10">
                    <h4 className="text-indigo-400 text-xs font-bold uppercase mb-1">Exportação</h4>
                    <p className="text-gray-400 text-[11px] leading-relaxed">Clique no botão de download para salvar a cifra e letra em formato PDF profissional para impressão.</p>
                </div>
            </div>
        </div>
    );
}
