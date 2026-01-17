# Backend - IsoMix Studio

Estrutura do backend seguindo a arquitetura **BMAD**.

## 📁 Estrutura de Pastas

```
backend/
├── business/           # 🏢 Business Layer
│   ├── __init__.py
│   ├── subscription.py    # Lógica de planos Free/Pro
│   ├── usage_limiter.py   # Controle de cotas
│   └── pricing.py         # Regras de monetização
│
├── model/              # 🧠 Model Layer
│   ├── __init__.py
│   ├── separator.py       # Interface para modelos de IA
│   ├── demucs_engine.py   # Implementação Demucs
│   ├── worker.py          # Celery worker
│   └── tasks.py           # Tarefas assíncronas
│
├── application/        # 🖥️ Application Layer
│   ├── __init__.py
│   ├── main.py            # FastAPI app
│   ├── routes/
│   │   ├── upload.py      # Endpoint de upload
│   │   ├── status.py      # Consulta de status
│   │   └── export.py      # Exportação de mix
│   ├── schemas/           # Pydantic models
│   └── middleware/        # CORS, Auth, etc.
│
├── domain/             # 📦 Domain Layer
│   ├── __init__.py
│   ├── models/
│   │   ├── project.py     # Entidade Project
│   │   ├── stem.py        # Entidade Stem
│   │   └── user.py        # Entidade User
│   ├── validators/
│   │   └── audio.py       # Validação de arquivos
│   ├── repositories/
│   │   └── project_repo.py
│   └── services/
│       └── storage.py     # Abstração de storage
│
├── storage/            # Arquivos temporários
│   ├── uploads/
│   ├── stems/
│   └── exports/
│
├── tests/              # Testes
│   ├── test_business/
│   ├── test_model/
│   ├── test_application/
│   └── test_domain/
│
├── alembic/            # Migrações de DB
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 🚀 Como Rodar

### Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Copiar .env
cp .env.example .env

# Rodar migrações
alembic upgrade head

# Iniciar API
uvicorn application.main:app --reload

# Em outro terminal, iniciar worker
celery -A model.worker worker --loglevel=info
```

### Com Docker

```bash
# Na raiz do projeto
docker-compose up backend worker
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=.
```
