# 🛠️ Comandos Úteis - IsoMix Studio

Referência rápida de comandos para desenvolvimento.

---

## 🐳 Docker

### Iniciar Serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Iniciar apenas backend + worker
docker-compose up -d backend worker db redis

# Iniciar com logs visíveis
docker-compose up
```

### Ver Logs

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas worker
docker-compose logs -f worker

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Parar e Limpar

```bash
# Parar serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Remover volumes também (CUIDADO: apaga banco de dados)
docker-compose down -v

# Rebuild completo
docker-compose build --no-cache
docker-compose up -d
```

### Executar Comandos nos Containers

```bash
# Shell no backend
docker-compose exec backend bash

# Shell no worker
docker-compose exec worker bash

# Executar comando Python
docker-compose exec backend python -c "print('Hello')"

# Ver status do Celery
docker-compose exec worker celery -A model.worker inspect active
```

---

## 🐍 Backend (Python)

### Ambiente Virtual

```bash
cd backend

# Criar venv
python3 -m venv venv

# Ativar
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Desativar
deactivate
```

### Dependências

```bash
# Instalar
pip install -r requirements.txt

# Adicionar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt

# Atualizar todas
pip install --upgrade -r requirements.txt
```

### Executar API

```bash
# Desenvolvimento (com reload)
uvicorn application.main:app --reload --port 8000

# Produção
uvicorn application.main:app --host 0.0.0.0 --port 8000 --workers 4

# Com logs detalhados
uvicorn application.main:app --reload --log-level debug
```

### Executar Worker Celery

```bash
# Worker padrão
celery -A model.worker worker --loglevel=info

# Com concurrency
celery -A model.worker worker --loglevel=info --concurrency=4

# Com autoreload (desenvolvimento)
watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A model.worker worker --loglevel=info
```

### Testes

```bash
# Rodar todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Teste específico
pytest tests/test_upload.py

# Com verbose
pytest -v

# Parar no primeiro erro
pytest -x
```

### Linting e Formatação

```bash
# Black (formatação)
black .

# Flake8 (linting)
flake8 .

# MyPy (type checking)
mypy .

# isort (organizar imports)
isort .
```

### Banco de Dados

```bash
# Criar tabelas
python -c "from domain.database import init_db; init_db()"

# Conectar ao PostgreSQL
psql -h localhost -U isomix_user -d isomix

# Dentro do psql
\dt                    # Listar tabelas
\d projects            # Descrever tabela
SELECT * FROM projects;
```

---

## ⚛️ Frontend (React)

### Dependências

```bash
cd frontend

# Instalar
npm install

# Adicionar nova dependência
npm install nome-do-pacote

# Adicionar dev dependency
npm install -D nome-do-pacote

# Atualizar todas
npm update

# Verificar pacotes desatualizados
npm outdated
```

### Executar

```bash
# Dev server
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Com porta customizada
npm run dev -- --port 3001
```

### Linting e Formatação

```bash
# ESLint
npm run lint

# ESLint com fix automático
npm run lint -- --fix

# Prettier (se configurado)
npx prettier --write "src/**/*.{ts,tsx}"
```

### Testes (quando implementados)

```bash
# Rodar testes
npm run test

# Com coverage
npm run test -- --coverage

# Watch mode
npm run test -- --watch
```

---

## 🗄️ Banco de Dados

### PostgreSQL

```bash
# Conectar
psql -h localhost -U isomix_user -d isomix

# Backup
pg_dump -h localhost -U isomix_user isomix > backup.sql

# Restore
psql -h localhost -U isomix_user isomix < backup.sql

# Listar databases
psql -h localhost -U isomix_user -l
```

### Redis

```bash
# Conectar
redis-cli

# Dentro do redis-cli
PING                   # Testar conexão
KEYS *                 # Listar todas as chaves
GET chave              # Obter valor
FLUSHALL               # Limpar tudo (CUIDADO!)
INFO                   # Informações do servidor

# Monitorar comandos em tempo real
redis-cli MONITOR
```

---

## 🔍 Debug e Troubleshooting

### Verificar Portas

```bash
# Linux/Mac
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Matar processo
kill -9 <PID>
```

### Logs do Sistema

```bash
# Logs do Docker
docker-compose logs -f

# Logs do sistema (Linux)
journalctl -u docker -f

# Uso de recursos
docker stats
```

### Limpar Cache

```bash
# Python
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node
rm -rf frontend/node_modules frontend/.next

# Docker
docker system prune -a
docker volume prune
```

---

## 📊 Monitoramento

### Celery

```bash
# Status dos workers
celery -A model.worker inspect active

# Estatísticas
celery -A model.worker inspect stats

# Tarefas registradas
celery -A model.worker inspect registered

# Flower (UI web para Celery)
pip install flower
celery -A model.worker flower
# Acesse: http://localhost:5555
```

### Recursos do Sistema

```bash
# CPU e memória
htop

# Uso de disco
df -h

# Processos Python
ps aux | grep python

# Processos Node
ps aux | grep node
```

---

## 🚀 Deploy

### Build para Produção

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm run build
# Arquivos em: frontend/dist/
```

### Variáveis de Ambiente

```bash
# Produção
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/db
export REDIS_URL=redis://host:6379/0
export ALLOWED_ORIGINS=https://seu-dominio.com
```

---

## 🧹 Manutenção

### Limpeza de Arquivos Antigos

```bash
# Manual
python -c "from model.tasks import cleanup_old_files; cleanup_old_files.delay(24)"

# Agendar com cron (Linux)
crontab -e
# Adicionar:
0 2 * * * cd /path/to/project && docker-compose exec -T worker python -c "from model.tasks import cleanup_old_files; cleanup_old_files.delay(24)"
```

### Backup Automático

```bash
# Script de backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U isomix_user isomix > backup_$DATE.sql
tar -czf storage_$DATE.tar.gz backend/storage/
```

---

## 📝 Git

### Commits

```bash
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "feat: adiciona funcionalidade X"

# Push
git push origin main
```

### Branches

```bash
# Criar branch
git checkout -b feature/nova-funcionalidade

# Trocar de branch
git checkout main

# Merge
git merge feature/nova-funcionalidade

# Deletar branch
git branch -d feature/nova-funcionalidade
```

---

## 🔧 Utilitários

### Gerar Secret Key

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
```

### Testar API

```bash
# Upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.mp3"

# Status
curl http://localhost:8000/api/status/PROJECT_ID

# Health check
curl http://localhost:8000/health
```

---

## 📚 Referências Rápidas

- **FastAPI Docs**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555
- **Frontend**: http://localhost:3000

---

<div align="center">
  <strong>Boa codificação! 💻</strong>
</div>
