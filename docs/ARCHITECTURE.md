# Arquitetura - IsoMix Studio

## Visão Geral

O IsoMix Studio segue a arquitetura **BMAD** (Business, Model, Application, Domain), garantindo separação de responsabilidades e escalabilidade.

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                    (React + TypeScript)                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ UploadPage   │  │  MixerPage   │  │ Components   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                          │                                  │
│                          │ HTTP/REST                        │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                    APPLICATION LAYER                        │
│                      (FastAPI)                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ /upload      │  │  /status     │  │  /export     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   BUSINESS    │  │    DOMAIN     │  │     MODEL     │
│               │  │               │  │               │
│ • UsageLimiter│  │ • Project     │  │ • Demucs      │
│ • Subscription│  │ • Stem        │  │ • Celery      │
│ • Pricing     │  │ • Validators  │  │ • Worker      │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
        ┌──────────────┐      ┌──────────────┐
        │  PostgreSQL  │      │    Redis     │
        │  (Metadata)  │      │   (Queue)    │
        └──────────────┘      └──────────────┘
```

---

## Camadas da Arquitetura

### 🖥️ Application Layer

**Responsabilidade**: Interface com o mundo externo (API REST)

**Componentes**:
- `main.py`: Aplicação FastAPI
- `routes/`: Endpoints HTTP
  - `upload.py`: Upload de arquivos
  - `status.py`: Consulta de status
  - `export.py`: Exportação de mix
- `schemas/`: Validação de request/response (Pydantic)
- `middleware/`: CORS, autenticação, etc.

**Tecnologias**: FastAPI, Pydantic, Uvicorn

---

### 🏢 Business Layer

**Responsabilidade**: Regras de negócio e monetização

**Componentes**:
- `usage_limiter.py`: Controle de cotas (Free vs Pro)
- `subscription.py`: Gestão de assinaturas
- `pricing.py`: Lógica de preços

**Regras Implementadas**:
- Limite de tamanho de arquivo por plano
- Limite de uploads diários
- Qualidade de exportação (MP3 vs WAV)
- Tempo de retenção de arquivos

---

### 🧠 Model Layer

**Responsabilidade**: Inteligência Artificial e processamento pesado

**Componentes**:
- `separator.py`: Interface abstrata para modelos
- `demucs_engine.py`: Implementação do Demucs
- `worker.py`: Configuração do Celery
- `tasks.py`: Tarefas assíncronas

**Fluxo de Processamento**:
1. Tarefa enfileirada no Redis
2. Worker consome tarefa
3. Carrega modelo Demucs na memória
4. Processa áudio (30-120s)
5. Salva 4 stems no storage
6. Atualiza status no banco

**Tecnologias**: Demucs, Celery, Redis

---

### 📦 Domain Layer

**Responsabilidade**: Entidades de domínio e lógica central

**Componentes**:
- `models/`: Entidades SQLAlchemy
  - `project.py`: Projeto de separação
  - `stem.py`: Faixa separada
- `validators/`: Validações de negócio
  - `audio.py`: Validação de arquivos
- `repositories/`: Acesso a dados
- `services/`: Serviços de domínio (storage, etc.)
- `database.py`: Configuração do SQLAlchemy

**Entidades Principais**:

```python
Project
├── id (UUID)
├── original_filename
├── status (pending, processing, ready, failed)
├── created_at
├── expires_at
└── stems (1:N)
    └── Stem
        ├── id
        ├── stem_type (vocals, drums, bass, other)
        └── file_path
```

---

## Fluxo de Dados

### 1. Upload de Arquivo

```
User → Frontend → API (/upload)
                    ↓
              Validate File
                    ↓
              Save to Storage
                    ↓
              Create Project (DB)
                    ↓
              Enqueue Task (Redis)
                    ↓
              Return 202 Accepted
```

### 2. Processamento Assíncrono

```
Worker → Pop Task (Redis)
           ↓
      Load Audio File
           ↓
      Run Demucs Model
           ↓
      Generate 4 Stems
           ↓
      Save Stems (Storage)
           ↓
      Update Project Status (DB)
```

### 3. Consulta de Status

```
Frontend → API (/status/{id})
             ↓
        Query DB
             ↓
        Return Status + Stems URLs
```

### 4. Exportação de Mix

```
Frontend → API (/export)
             ↓
        Load Stems
             ↓
        Apply Volumes/Mutes (ffmpeg)
             ↓
        Generate Mix File
             ↓
        Return Download URL
```

---

## Decisões Arquiteturais

### Por que BMAD?

1. **Separação de Responsabilidades**: Cada camada tem um propósito claro
2. **Testabilidade**: Camadas podem ser testadas independentemente
3. **Escalabilidade**: Workers podem ser escalados horizontalmente
4. **Manutenibilidade**: Mudanças em uma camada não afetam outras

### Por que Celery?

- Processamento de IA é **lento** (30-120s)
- Não podemos bloquear a API esperando
- Celery permite **processamento assíncrono** em background
- Fácil de escalar (adicionar mais workers)

### Por que PostgreSQL + Redis?

- **PostgreSQL**: Metadados estruturados (projetos, stems)
- **Redis**: Fila de tarefas (rápido, em memória)

### Por que Demucs?

- **Alta qualidade** de separação
- **Open source** (Meta Research)
- **Bem mantido** e documentado
- Alternativa: Spleeter (mais rápido, menor qualidade)

---

## Escalabilidade

### Horizontal Scaling

```
┌─────────────┐
│   Nginx     │ (Load Balancer)
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
   ▼       ▼       ▼       ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ API │ │ API │ │ API │ │ API │ (Múltiplas instâncias)
└─────┘ └─────┘ └─────┘ └─────┘
   │       │       │       │
   └───┬───┴───────┴───────┘
       │
   ┌───┴───┐
   │ Redis │ (Fila compartilhada)
   └───┬───┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
   ▼       ▼       ▼       ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│Worker 1││Worker 2││Worker 3││Worker 4│ (Múltiplos workers)
└────────┘└────────┘└────────┘└────────┘
```

### Otimizações Futuras

1. **Cache de Modelos**: Manter Demucs em memória
2. **CDN**: Servir stems via CloudFront/CloudFlare
3. **GPU Workers**: Acelerar processamento com CUDA
4. **Streaming**: Processar stems progressivamente
5. **WebSockets**: Atualização de status em tempo real

---

## Segurança

### Implementado

- ✅ Validação de MIME type real (não apenas extensão)
- ✅ Limite de tamanho de arquivo
- ✅ Isolamento de arquivos por sessão UUID
- ✅ CORS configurável
- ✅ Garbage collection automático

### TODO

- ⬜ Autenticação JWT
- ⬜ Rate limiting por IP
- ⬜ Signed URLs para download
- ⬜ Criptografia de arquivos em repouso
- ⬜ Audit logs

---

## Monitoramento

### Métricas Importantes

- **Latência de Upload**: Tempo do upload até enfileiramento
- **Tempo de Processamento**: Tempo da IA para separar
- **Taxa de Erro**: % de processamentos que falharam
- **Uso de Storage**: Espaço ocupado pelos arquivos
- **Fila do Celery**: Tarefas pendentes

### Ferramentas Sugeridas

- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização
- **Sentry**: Tracking de erros
- **Flower**: Monitoramento do Celery

---

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
