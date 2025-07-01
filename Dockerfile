# Use Python 3.11 como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DBT_PROFILES_DIR=/app/DGU

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs && \
    mkdir -p /app/DGU/seeds && \
    mkdir -p /app/DGU/target && \
    mkdir -p /app/credentials

# Definir permissões para o entrypoint
RUN chmod +x entrypoint.sh

# Expor porta (se necessário para futuras extensões)
EXPOSE 8080

# Definir entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Comando padrão
CMD ["python", "main.py"]
