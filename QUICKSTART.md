# 🚀 Guia de Início Rápido - IsoMix Studio

Este guia vai te ajudar a colocar o IsoMix Studio rodando localmente em poucos minutos.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** e **Docker Compose** (recomendado) OU
- **Python 3.11+**, **Node.js 18+**, **PostgreSQL** e **Redis** (instalação manual)

---

## 🐳 Opção 1: Docker (Recomendado)

### 1️⃣ Clone e Configure

```bash
# Clone o repositório
cd /home/clenio/Documentos/Meusagentes/audio-fenix

# Configure variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2️⃣ Inicie os Serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 3️⃣ Acesse a Aplicação

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4️⃣ Parar os Serviços

```bash
docker-compose down
```

---

## 💻 Opção 2: Instalação Manual

### Backend (Python)

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Edite o .env com suas configurações

# Iniciar PostgreSQL e Redis (em terminais separados)
# Você precisa ter eles instalados no sistema

# Iniciar API
uvicorn application.main:app --reload --port 8000

# Em OUTRO terminal, iniciar Worker Celery
cd backend
source venv/bin/activate
celery -A model.worker worker --loglevel=info
```

### Frontend (React)

```bash
cd frontend

# Instalar dependências
npm install

# Configurar .env
cp .env.example .env

# Iniciar dev server
npm run dev
```

---

## 🧪 Testando a Aplicação

### 1. Upload de Áudio

1. Acesse http://localhost:3000
2. Faça upload de um arquivo MP3, WAV ou FLAC (máx. 20MB)
3. Aguarde o processamento (30-120 segundos)

### 2. Mixer

1. Após o processamento, você verá 4 canais:
   - 🎤 **Vocal**
   - 🥁 **Bateria**
   - 🎸 **Baixo**
   - 🎹 **Outros**

2. Controles disponíveis:
   - **Fader**: Ajustar volume (0-100%)
   - **M (Mute)**: Silenciar canal
   - **S (Solo)**: Isolar apenas esse canal

3. Clique em **"Exportar Mix"** para baixar o resultado

---

## 📊 Verificando os Serviços

### Health Checks

```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Redis
redis-cli ping

# PostgreSQL
psql -h localhost -U isomix_user -d isomix -c "SELECT 1;"
```

### Logs

```bash
# Docker
docker-compose logs backend
docker-compose logs worker
docker-compose logs frontend

# Manual
# Os logs aparecem nos terminais onde você executou os comandos
```

---

## 🐛 Troubleshooting

### Erro: "Port already in use"

```bash
# Verificar o que está usando a porta
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# Matar o processo
kill -9 <PID>
```

### Erro: "ModuleNotFoundError: No module named 'demucs'"

```bash
# Reinstalar dependências
cd backend
pip install -r requirements.txt
```

### Erro: "Cannot connect to database"

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Ou manualmente
sudo systemctl status postgresql
```

### Erro: "Celery worker not processing tasks"

```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Verificar logs do worker
docker-compose logs worker

# Reiniciar worker
docker-compose restart worker
```

### Erro: "ffmpeg not found"

```bash
# Instalar ffmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

---

## 📁 Estrutura de Arquivos Gerados

Durante o uso, a aplicação cria arquivos em:

```
backend/storage/
├── uploads/          # Arquivos originais enviados
│   └── <project-id>/
│       └── song.mp3
├── stems/            # Stems gerados pela IA
│   └── <project-id>/
│       ├── vocals.wav
│       ├── drums.wav
│       ├── bass.wav
│       └── other.wav
└── exports/          # Mixagens exportadas
    └── <project-id>/
        └── mix_<project-id>.mp3
```

**Nota**: Arquivos são automaticamente deletados após 24 horas (Free) ou 30 dias (Pro).

---

## 🔧 Configurações Avançadas

### Trocar Modelo de IA

Edite `backend/.env`:

```bash
# Opções: demucs, spleeter
AI_MODEL=demucs

# Qualidade do Demucs: htdemucs, htdemucs_ft, mdx_extra
AI_MODEL_QUALITY=htdemucs
```

### Ajustar Limites de Upload

Edite `backend/.env`:

```bash
MAX_FILE_SIZE_FREE_MB=20
MAX_FILE_SIZE_PRO_MB=100
MAX_UPLOADS_PER_DAY_FREE=5
```

### Configurar CORS

Edite `backend/.env`:

```bash
ALLOWED_ORIGINS=http://localhost:3000,https://seu-dominio.com
```

---

## 📚 Próximos Passos

1. ✅ Leia o [PRD](./docs/PRD.md) para entender a arquitetura
2. ✅ Veja as [User Stories](./docs/USER_STORIES.md) para funcionalidades planejadas
3. ✅ Consulte o [Diagrama de Sequência](./docs/SEQUENCE_DIAGRAM.md) para entender o fluxo
4. ✅ Explore a [API Docs](http://localhost:8000/docs) para integração

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso [README principal](./README.md) para mais detalhes.

---

## 📧 Suporte

Encontrou algum problema? Abra uma issue no GitHub ou entre em contato.

---

<div align="center">
  <strong>Bom uso! 🎵</strong>
</div>
