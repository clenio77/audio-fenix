# 🎛️ IsoMix Studio

> **Audio Source Separation WebApp** - Separe, mixe e exporte faixas de áudio com IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Sobre o Projeto

O **IsoMix Studio** é uma plataforma SaaS que utiliza Deep Learning para separar fontes sonoras em arquivos de áudio. Diferente de conversores comuns, oferece uma **interface de Mesa de Som Digital** no navegador, permitindo manipular volumes, isolar canais e exportar mixagens personalizadas em tempo real.

### ✨ Funcionalidades Principais

- 🎵 **Separação de Áudio com IA**: Decompõe músicas em Vocal, Bateria, Baixo e Outros
- 🎛️ **Mixer Profissional**: Interface visual simulando uma mesa de som real
- 🎚️ **Controles Avançados**: Volume, Mute, Solo e Pan para cada canal
- 📊 **Visualização de Waveform**: Veja a forma de onda de cada faixa
- 💾 **Exportação Flexível**: Baixe o mix customizado ou stems individuais
- ⚡ **Processamento Assíncrono**: Upload rápido, processamento em background

---

## 🏗️ Arquitetura BMAD

O projeto segue a metodologia **BMAD** (Business, Model, Application, Domain):

```
audio-fenix/
├── backend/                    # Backend Python (FastAPI)
│   ├── business/              # 🏢 Regras de negócio e monetização
│   ├── model/                 # 🧠 Modelos de IA (Demucs/Spleeter)
│   ├── application/           # 🖥️ API e orquestração
│   └── domain/                # 📦 Entidades e validações
├── frontend/                   # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── pages/             # Páginas da aplicação
│   │   ├── services/          # Integração com API
│   │   └── store/             # Gerenciamento de estado (Zustand)
├── docs/                       # Documentação
│   ├── PRD.md                 # Product Requirements Document
│   ├── USER_STORIES.md        # Histórias de Usuário
│   └── SEQUENCE_DIAGRAM.md    # Diagramas de Sequência
└── docker/                     # Configurações Docker
```

---

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Redis** (para fila de jobs)
- **PostgreSQL** (para metadados)

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/seu-usuario/audio-fenix.git
cd audio-fenix
```

### 2️⃣ Configure as Variáveis de Ambiente

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### 3️⃣ Inicie com Docker Compose

```bash
docker-compose up -d
```

Acesse:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

---

## 🛠️ Desenvolvimento Local

### Backend (FastAPI)

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar migrações
alembic upgrade head

# Iniciar servidor
uvicorn application.main:app --reload --port 8000

# Em outro terminal, iniciar worker Celery
celery -A model.worker worker --loglevel=info
```

### Frontend (React + Vite)

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar dev server
npm run dev
```

---

## 📚 Documentação

- [📄 PRD - Product Requirements Document](./docs/PRD.md)
- [📝 User Stories - Histórias de Usuário](./docs/USER_STORIES.md)
- [🔄 Sequence Diagram - Fluxo de Processamento](./docs/SEQUENCE_DIAGRAM.md)
- [🏗️ Architecture - Arquitetura Detalhada](./docs/ARCHITECTURE.md)
- [🔌 API Reference - Referência da API](./docs/API.md)

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend

```bash
cd frontend
npm run test
npm run test:e2e  # Testes E2E com Playwright
```

---

## 🎯 Roadmap

### ✅ Fase 1 - MVP (Atual)
- [x] Upload de arquivos MP3/WAV
- [x] Processamento com Demucs (4 stems)
- [x] Mixer básico com Volume + Mute
- [x] Exportação de mix final

### 🚧 Fase 2 - Aprimoramentos
- [ ] Visualização de waveform
- [ ] Controles de Pan (L/R)
- [ ] Botão Solo
- [ ] Download de stems individuais

### 📅 Fase 3 - Profissionalização
- [ ] Efeitos (Reverb, EQ)
- [ ] Histórico de projetos
- [ ] Planos Free/Pro
- [ ] API para desenvolvedores

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [Demucs](https://github.com/facebookresearch/demucs) - Meta Research (modelo de IA)
- [Wavesurfer.js](https://wavesurfer-js.org/) - Visualização de áudio
- [FastAPI](https://fastapi.tiangolo.com/) - Framework backend
- [React](https://reactjs.org/) - Framework frontend

---

## 📧 Contato

**Seu Nome** - [@seu_twitter](https://twitter.com/seu_twitter) - email@example.com

**Link do Projeto**: [https://github.com/seu-usuario/audio-fenix](https://github.com/seu-usuario/audio-fenix)

---

<div align="center">
  <strong>Feito com ❤️ e 🎵</strong>
</div>
