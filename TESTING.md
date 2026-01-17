# 🧪 Guia de Testes - IsoMix Studio

Este documento descreve como executar os testes automatizados do projeto.

---

## 📋 Visão Geral

O projeto possui testes em duas camadas:

| Camada | Framework | Cobertura |
|--------|-----------|-----------|
| **Backend (Python)** | pytest | UsageLimiter, AudioValidator, API, Models |
| **Frontend (TypeScript)** | Vitest | MixerChannel, API Service |

---

## 🐍 Testes Backend (Python)

### Instalação de Dependências

```bash
cd backend
pip install -r requirements.txt
```

### Executar Todos os Testes

```bash
# Dentro do container Docker
docker-compose exec backend pytest

# Ou localmente (se ambiente virtual configurado)
cd backend
pytest
```

### Executar com Cobertura

```bash
pytest --cov=business --cov=domain --cov=application --cov-report=html
```

### Executar Testes Específicos

```bash
# Apenas testes do UsageLimiter (Business Layer)
pytest tests/test_usage_limiter.py -v

# Apenas testes do AudioValidator (Domain Layer)
pytest tests/test_audio_validator.py -v

# Apenas testes da API (Application Layer)
pytest tests/test_api.py -v

# Apenas testes dos Models (Domain Layer)
pytest tests/test_models.py -v
```

### Executar por Markers

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Excluir testes lentos
pytest -m "not slow"
```

### Estrutura de Testes Backend

```
backend/tests/
├── __init__.py
├── conftest.py          # Fixtures compartilhadas
├── test_usage_limiter.py   # Testes Business Layer
├── test_audio_validator.py # Testes Domain Layer (Validators)
├── test_models.py          # Testes Domain Layer (Models)
└── test_api.py             # Testes Application Layer (API)
```

---

## ⚛️ Testes Frontend (TypeScript)

### Instalação de Dependências

```bash
cd frontend
npm install
```

### Executar Todos os Testes

```bash
# Modo watch (desenvolvimento)
npm test

# Executar uma vez
npm run test:run
```

### Executar com Cobertura

```bash
npm run test:coverage
```

### Executar Testes Específicos

```bash
# Apenas testes de um arquivo
npm test -- MixerChannel

# Apenas testes de serviços
npm test -- api.test
```

### Estrutura de Testes Frontend

```
frontend/src/
├── components/
│   └── __tests__/
│       └── MixerChannel.test.tsx
├── services/
│   └── __tests__/
│       └── api.test.ts
└── test/
    └── setup.ts          # Configuração global
```

---

## 🐳 Testes via Docker

### Executar Testes do Backend no Container

```bash
# Subir containers
docker-compose up -d

# Executar testes
docker-compose exec backend pytest -v

# Com cobertura
docker-compose exec backend pytest --cov --cov-report=term-missing
```

### Criar Container Apenas para Testes

```bash
docker-compose run --rm backend pytest
```

---

## 📊 Casos de Teste

### Backend - Business Layer (UsageLimiter)

- ✅ Planos de assinatura (FREE, PRO)
- ✅ Limites de tamanho de arquivo por plano
- ✅ Limites de duração de áudio por plano
- ✅ Cotas diárias de upload
- ✅ Formato de exportação por plano
- ✅ Marca d'água (watermark)
- ✅ Tempo de retenção de arquivos
- ✅ Mensagem de upgrade

### Backend - Domain Layer (AudioValidator)

- ✅ Validação de formato (MIME type)
- ✅ Fallback para extensão de arquivo
- ✅ Extração de metadados (ffprobe)
- ✅ Validação de tamanho
- ✅ Validação de duração

### Backend - Application Layer (API)

- ✅ Health check endpoints
- ✅ Upload de arquivo (sucesso e erros)
- ✅ Consulta de status
- ✅ Exportação de mix
- ✅ Configuração CORS
- ✅ Documentação OpenAPI

### Frontend - Components

- ✅ MixerChannel renderização
- ✅ Labels corretos por stem type
- ✅ Ícones corretos
- ✅ Interação com botões Mute/Solo
- ✅ Estados visuais (active class)
- ✅ Acessibilidade (aria-labels)

### Frontend - Services

- ✅ API service métodos
- ✅ Construção de URLs
- ✅ Headers corretos

---

## 🎯 Metas de Cobertura

| Camada | Meta | Atual |
|--------|------|-------|
| Business Layer | 90% | - |
| Domain Layer | 85% | - |
| Application Layer | 80% | - |
| Frontend Components | 80% | - |

---

## 🔧 Configurações

### pytest.ini (Backend)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --color=yes
```

### vite.config.ts (Frontend)

```typescript
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: ['./src/test/setup.ts'],
  include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
}
```

---

## 🚀 CI/CD (Futuro)

Para integrar com GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run test:run
```

---

## 📝 Boas Práticas

1. **Nomenclatura**: Use nomes descritivos que expliquem o comportamento esperado
2. **Arrange-Act-Assert**: Organize testes em setup, execução e verificação
3. **Mocks**: Use mocks para dependências externas (Celery, ffprobe)
4. **Fixtures**: Reutilize configurações via fixtures do pytest
5. **Isolamento**: Cada teste deve ser independente
6. **Cobertura**: Mantenha cobertura acima de 80%

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"

```bash
# Certifique-se de estar no diretório correto
cd backend
export PYTHONPATH=.
pytest
```

### Erro: "Database connection failed"

Os testes usam SQLite em memória. Verifique se `conftest.py` está configurado corretamente.

### Erro: "Cannot find module 'vitest'"

```bash
cd frontend
npm install
```

---

*Última atualização: 25 de Dezembro de 2025*
