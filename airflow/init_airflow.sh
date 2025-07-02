#!/bin/bash

# Script de inicialização do Airflow para projeto DGU
set -e

echo "🚀 Inicializando Apache Airflow 3.0 para projeto DGU"
echo "=================================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verificar se credenciais existem
if [ ! -f "credentials/bigquery-credentials.json" ]; then
    echo "❌ Credenciais do BigQuery não encontradas!"
    echo "   Copie suas credenciais para: credentials/bigquery-credentials.json"
    exit 1
fi

# Verificar se profiles.yml existe
if [ ! -f "DGU/profiles.yml" ]; then
    echo "❌ Arquivo profiles.yml não encontrado!"
    echo "   Copie e configure: cp DGU/profiles.yml.example DGU/profiles.yml"
    exit 1
fi

# Definir AIRFLOW_UID se não estiver definido
export AIRFLOW_UID=$(id -u)
echo "📋 AIRFLOW_UID definido como: $AIRFLOW_UID"

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p airflow/logs
mkdir -p airflow/dags
mkdir -p airflow/plugins
mkdir -p airflow/config

# Definir permissões corretas
echo "🔐 Configurando permissões..."
chmod -R 755 airflow/
chmod 600 credentials/bigquery-credentials.json

# Construir imagem do Airflow
echo "🏗️ Construindo imagem do Airflow..."
docker-compose -f docker-compose-airflow.yml build

# Inicializar banco de dados do Airflow
echo "🗄️ Inicializando banco de dados do Airflow..."
docker-compose -f docker-compose-airflow.yml up airflow-init

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Iniciar serviços do Airflow
echo "🚀 Iniciando serviços do Airflow..."
docker-compose -f docker-compose-airflow.yml up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar se serviços estão rodando
echo "🔍 Verificando status dos serviços..."
docker-compose -f docker-compose-airflow.yml ps

# Configurar conexões e variáveis
echo "⚙️ Configurando conexões e variáveis do Airflow..."
docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver python /opt/airflow/project/airflow/setup_airflow_connections.py

echo ""
echo "🎉 Airflow inicializado com sucesso!"
echo "=================================================="
echo ""
echo "📊 Informações de acesso:"
echo "• Interface Web: http://localhost:8080"
echo "• Usuário: airflow"
echo "• Senha: airflow"
echo ""
echo "📋 DAGs disponíveis:"
echo "• dgu_futebol_pipeline - Pipeline principal (Terças e Sextas às 09:00)"
echo "• dgu_monitoring - Monitoramento diário (Diariamente às 10:00)"
echo ""
echo "🔧 Comandos úteis:"
echo "• Ver logs: docker-compose -f docker-compose-airflow.yml logs -f"
echo "• Parar serviços: docker-compose -f docker-compose-airflow.yml down"
echo "• Reiniciar: docker-compose -f docker-compose-airflow.yml restart"
echo ""
echo "📚 Próximos passos:"
echo "1. Acesse http://localhost:8080 no seu navegador"
echo "2. Faça login com usuário 'airflow' e senha 'airflow'"
echo "3. Ative as DAGs na interface web"
echo "4. Execute um teste manual das DAGs"
echo ""
