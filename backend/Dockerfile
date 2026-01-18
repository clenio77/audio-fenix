FROM python:3.10-slim

# Instalar dependências do sistema para processamento de áudio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir email-validator python-jose[cryptography] passlib[bcrypt]

# Copiar código
COPY . .

# Criar diretórios de storage
RUN mkdir -p storage/uploads storage/stems storage/exports

# Expor porta
EXPOSE 8000

# Comando padrão (será sobrescrito no docker-compose)
CMD ["uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]
