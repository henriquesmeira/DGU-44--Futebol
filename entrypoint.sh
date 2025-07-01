#!/bin/bash

# Script de inicialização para o container DGU Futebol
set -e

echo "🐳 Iniciando container DGU - Pipeline de Dados de Futebol"
echo "=================================================="

# Verificar se as credenciais do BigQuery existem
if [ ! -f "/app/credentials/bigquery-credentials.json" ]; then
    echo "❌ ERRO: Arquivo de credenciais do BigQuery não encontrado!"
    echo "   Certifique-se de que o arquivo está em ./credentials/bigquery-credentials.json"
    exit 1
fi

# Verificar se o profiles.yml existe
if [ ! -f "/app/DGU/profiles.yml" ]; then
    echo "❌ ERRO: Arquivo profiles.yml não encontrado!"
    echo "   Certifique-se de copiar DGU/profiles.yml.example para DGU/profiles.yml"
    echo "   e configurar suas credenciais."
    exit 1
fi

# Configurar variáveis de ambiente
export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/bigquery-credentials.json"
export DBT_PROFILES_DIR="/app/DGU"

echo "✅ Credenciais configuradas"
echo "✅ Ambiente dbt configurado"

# Verificar conectividade com BigQuery (opcional)
echo "🔍 Verificando conectividade com BigQuery..."
python -c "
from google.cloud import bigquery
import os
try:
    client = bigquery.Client()
    print('✅ Conexão com BigQuery estabelecida com sucesso!')
except Exception as e:
    print(f'❌ Erro na conexão com BigQuery: {e}')
    exit(1)
" || exit 1

# Criar diretórios necessários
mkdir -p /app/logs
mkdir -p /app/DGU/seeds
mkdir -p /app/DGU/target

echo "📁 Diretórios criados"

# Verificar se dbt está funcionando
echo "🔧 Verificando instalação do dbt..."
cd /app/DGU
dbt --version || exit 1

echo "✅ dbt verificado com sucesso"

# Voltar para o diretório principal
cd /app

echo "🚀 Ambiente configurado! Executando comando..."
echo "=================================================="

# Executar o comando passado como argumento
exec "$@"
