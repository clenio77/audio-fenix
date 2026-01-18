import { useEffect, useRef } from 'react';
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay';

interface SheetMusicViewerProps {
    xmlUrl: string;
    currentTime: number;
    isPlaying: boolean;
}

export default function SheetMusicViewer({ xmlUrl, currentTime, isPlaying }: SheetMusicViewerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const osmdRef = useRef<OpenSheetMusicDisplay | null>(null);

    useEffect(() => {
        if (containerRef.current && !osmdRef.current) {
            osmdRef.current = new OpenSheetMusicDisplay(containerRef.current, {
                autoResize: true,
                drawTitle: false,
                drawSubtitle: false,
                drawComposer: false,
                drawLyricist: false,
                drawCredits: false,
                backend: 'svg',
                renderSelectionColor: '#ec4899', // Pink-500
            });
        }

        const loadScore = async () => {
            if (osmdRef.current && xmlUrl) {
                try {
                    await osmdRef.current.load(xmlUrl);
                    osmdRef.current.render();
                } catch (error) {
                    console.error('Error loading Sheet Music XML:', error);
                }
            }
        };

        loadScore();

        return () => {
            // Cleanup if needed
        };
    }, [xmlUrl]);

    // Sincronização visual (O OSMD não sincroniza automaticamente via currentTime sem um playback engine, 
    // mas aqui podemos preparar o cursor para futuras implementações)
    useEffect(() => {
        if (osmdRef.current && isPlaying) {
            // Lógica de cursor pode ser adicionada aqui
        }
    }, [currentTime, isPlaying]);

    return (
        <div className="w-full bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-purple-400 tracking-widest uppercase flex items-center gap-2">
                    <span className="text-xl">🎼</span> Visualizador de Partitura
                </h3>
                <span className="text-[10px] text-gray-500 bg-black/30 px-2 py-1 rounded-full border border-white/5">
                    DYNAMIC RENDERING
                </span>
            </div>
            <div
                ref={containerRef}
                className="w-full min-h-[400px] bg-white rounded-xl shadow-inner overflow-x-auto"
                style={{ filter: 'invert(1) hue-rotate(180deg) brightness(1.2)' }} // Dark mode para a partitura
            />
            <p className="mt-4 text-[11px] text-gray-500 text-center italic">
                A partitura é gerada via IA e pode conter imprecisões rítmicas.
            </p>
        </div>
    );
}
