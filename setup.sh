#!/bin/bash

# Script de Setup - IsoMix Studio
# Este script prepara o ambiente para desenvolvimento

set -e

echo "🎵 IsoMix Studio - Setup"
echo "========================"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
echo -e "${YELLOW}1. Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi
echo -e "${GREEN}✓ Docker instalado${NC}"

# Verificar Docker Compose
echo -e "${YELLOW}2. Verificando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale o Docker Compose primeiro."
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose instalado${NC}"

# Criar arquivos .env se não existirem
echo -e "${YELLOW}3. Configurando variáveis de ambiente...${NC}"

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ backend/.env criado${NC}"
else
    echo "  backend/.env já existe"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ frontend/.env criado${NC}"
else
    echo "  frontend/.env já existe"
fi

# Criar diretórios de storage
echo -e "${YELLOW}4. Criando diretórios de storage...${NC}"
mkdir -p backend/storage/{uploads,stems,exports}
touch backend/storage/uploads/.gitkeep
touch backend/storage/stems/.gitkeep
touch backend/storage/exports/.gitkeep
echo -e "${GREEN}✓ Diretórios criados${NC}"

# Build das imagens Docker
echo -e "${YELLOW}5. Fazendo build das imagens Docker...${NC}"
echo "  (Isso pode levar alguns minutos na primeira vez)"
docker-compose build

echo ""
echo -e "${GREEN}✅ Setup concluído!${NC}"
echo ""
echo "Para iniciar o projeto:"
echo "  docker-compose up -d"
echo ""
echo "Para ver os logs:"
echo "  docker-compose logs -f"
echo ""
echo "Acessar:"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
