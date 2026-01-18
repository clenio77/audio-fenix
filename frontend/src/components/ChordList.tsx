import { ChordInfo } from '@/types';
import { Music } from 'lucide-react';

interface ChordListProps {
    chords: ChordInfo[];
    currentTime: number;
}

export default function ChordList({ chords, currentTime }: ChordListProps) {
    // Agrupar acordes por proximidade ou simplesmente listar
    // Para uma "cifra", podemos mostrar blocos de acordes

    return (
        <div className="w-full bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-sm font-bold text-amber-400 tracking-widest uppercase flex items-center gap-2">
                    <Music className="w-5 h-5" /> Cifra Completa (IA)
                </h3>
                <span className="text-[10px] text-amber-500/50 bg-amber-500/10 px-2 py-1 rounded-full border border-amber-500/20">
                    CHORD SEQUENCE
                </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {chords.map((chord, index) => {
                    const isActive = currentTime >= chord.time && currentTime <= (chord.time + chord.duration);

                    return (
                        <div
                            key={`${chord.chord}-${index}`}
                            className={`
                relative p-4 rounded-xl border transition-all duration-300 text-center
                ${isActive
                                    ? 'bg-amber-500 border-amber-300 shadow-lg shadow-amber-500/40 scale-105 z-10'
                                    : 'bg-black/20 border-white/5 text-gray-400 hover:border-white/20'
                                }
              `}
                        >
                            <span className={`text-xl font-bold font-mono ${isActive ? 'text-black' : 'text-amber-400/80'}`}>
                                {chord.chord}
                            </span>
                            <div className={`text-[9px] mt-1 ${isActive ? 'text-black/60' : 'text-gray-600'}`}>
                                {Math.floor(chord.time / 60)}:{(chord.time % 60).toFixed(0).padStart(2, '0')}
                            </div>

                            {isActive && (
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full animate-ping" />
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="mt-6 pt-4 border-t border-white/5 flex gap-4 text-[10px] text-gray-500 italic">
                <p>💡 Toque a música para acompanhar a cifra em tempo real.</p>
                <p>⚠️ Detecção automática via processamento de harmonia.</p>
            </div>
        </div>
    );
}
