# Frontend - IsoMix Studio

Interface web do IsoMix Studio construída com React, TypeScript e Vite.

## 🚀 Quick Start

```bash
# Instalar dependências
npm install

# Copiar .env
cp .env.example .env

# Iniciar dev server
npm run dev
```

Acesse: http://localhost:3000

## 📁 Estrutura

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizáveis
│   │   └── MixerChannel.tsx
│   ├── pages/             # Páginas da aplicação
│   │   ├── UploadPage.tsx
│   │   └── MixerPage.tsx
│   ├── services/          # Integração com API
│   │   └── api.ts
│   ├── store/             # Gerenciamento de estado (Zustand)
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── App.tsx            # Componente principal
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globais
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🎨 Stack Tecnológica

- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **Radix UI** - Componentes acessíveis
- **Wavesurfer.js** - Visualização de áudio
- **Axios** - Cliente HTTP
- **Zustand** - State management

## 🧪 Scripts

```bash
npm run dev      # Dev server
npm run build    # Build para produção
npm run preview  # Preview do build
npm run lint     # Lint com ESLint
```

## 🎛️ Componentes Principais

### UploadPage
- Drag-and-drop de arquivos
- Validação de formato e tamanho
- Integração com API de upload

### MixerPage
- Polling de status do processamento
- 4 canais de mixer (Vocal, Drums, Bass, Other)
- Controles de volume, mute e solo
- Exportação de mix customizado

### MixerChannel
- Fader vertical de volume
- Botões de mute e solo
- Indicador visual de nível
- Placeholder para waveform

## 🔌 Integração com Backend

A comunicação com o backend é feita através do `apiService`:

```typescript
import { apiService } from '@/services/api'

// Upload
const response = await apiService.uploadAudio(file)

// Status
const project = await apiService.getProjectStatus(projectId)

// Export
const exportData = await apiService.exportMix(request)
```

## 🎨 Customização de Cores

As cores do mixer podem ser customizadas em `tailwind.config.js`:

```javascript
colors: {
  mixer: {
    bg: '#1a1a1a',
    panel: '#2a2a2a',
    accent: '#00d9ff',
    vocal: '#3b82f6',
    drums: '#ef4444',
    bass: '#10b981',
    other: '#f59e0b',
  }
}
```
