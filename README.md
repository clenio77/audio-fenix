# 🎛️ IsoMix Studio

> **Audio Source Separation WebApp** - Separe, mixe e exporte faixas de áudio com IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)

---

## 📖 Sobre o Projeto

O **IsoMix Studio** é uma plataforma SaaS que utiliza Deep Learning para separar fontes sonoras em arquivos de áudio. Diferente de conversores comuns, oferece uma **interface de Mesa de Som Digital** no navegador, permitindo manipular volumes, isolar canais e exportar mixagens personalizadas em tempo real.

### ✨ Funcionalidades Principais

- 🎵 **Separação de Áudio com IA**: Decompõe músicas em Vocal, Bateria, Baixo e Outros.
- 🎼 **Transcrição de Partituras (NOVO)**: Gera automaticamente partituras (MusicXML) e arquivos MIDI a partir do áudio.
- 🎛️ **Mixer Profissional**: Interface visual simulando uma mesa de som real.
- 🎚️ **Controles Avançados**: Volume, Mute, Solo e Pan para cada canal.
- 📊 **Visualização de Waveform**: Veja a forma de onda de cada faixa.
- 💾 **Exportação Flexível**: Baixe o mix customizado ou stems individuais.
- ⚡ **Processamento Assíncrono**: Upload rápido, processamento em background via Celery.

---

## 🚀 Como Executar a Aplicação

> **Nota:** Esta aplicação **NÃO** está configurada para iniciar automaticamente com o computador. Você deve executar um dos métodos abaixo sempre que desejar usá-la.

### 🐳 Opção A: Via Docker (Recomendado)

O Docker cuida de todas as dependências (Banco de Dados, Redis, IA, Backend e Frontend).

1. **Inicie os containers pela primeira vez (ou se houver mudanças no código):**
   ```bash
   docker-compose up --build
   ```
2. **Para rodar em segundo plano:**
   ```bash
   docker-compose up -d
   ```
3. **Acesse:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 💻 Opção B: Desenvolvimento Manual (Sem Docker)

Você precisará de terminais separados para rodar cada serviço:

#### 1. Pré-requisitos
- Redis e PostgreSQL ativos no sistema.
- Se não tiver, inicie-os via docker: `docker-compose up -d db redis`

#### 2. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn application.main:app --reload --port 8000
```

#### 3. Worker Celery (Processamento de IA)
```bash
cd backend
source .venv/bin/activate
celery -A model.worker worker --loglevel=info
```

#### 4. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## 🏗️ Arquitetura Detalhada

O projeto segue a metodologia **BMAD** (Business, Model, Application, Domain):

```
audio-fenix/
├── backend/                    # Backend Python (FastAPI)
│   ├── business/              # 🏢 Regras de negócio e limites
│   ├── model/                 # 🧠 Modelos de IA (Demucs + Transcrição)
│   ├── application/           # 🖥️ API e Gerenciamento de Tasks
│   └── domain/                # 📦 Banco de Dados e Entidades
├── frontend/                   # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/        # Mixer, Waveforms, SheetMusic
│   │   ├── pages/             # Layouts Principais
│   │   └── services/          # Conexão com API
└── docs/                       # Documentação Técnica
```

---

## 🎯 Roadmap

### ✅ Fase 1 - MVP
- [x] Upload de arquivos MP3/WAV
- [x] Processamento com Demucs (4 stems)
- [x] Mixer básico com Volume + Mute
- [x] Detecção de BPM e Acordes

### 🎼 Fase 2 - Transcrição Musical (Ativa)
- [x] Geração de arquivos MIDI
- [x] Geração de Partituras (MusicXML)
- [x] Visualizador de Partitura direto no navegador
- [ ] Pitch Shift Real-time (Em desenvolvimento)

### 📅 Fase 3 - Profissionalização
- [ ] Efeitos de áudio (Reverb, EQ)
- [ ] Histórico de projetos por usuário
- [ ] Sistema de Planos/Créditos

---

## 🤝 Repositório Oficial
**GitHub**: [https://github.com/clenio77/audio-fenix](https://github.com/clenio77/audio-fenix)

---
<div align="center">
  <strong>Feito com ❤️ e 🎵</strong>
</div>
