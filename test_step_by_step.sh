#!/bin/bash

# Script para testar dbt passo a passo
echo "=== TESTE PASSO A PASSO ==="
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "DGU" ]; then
    echo "❌ Erro: Diretório DGU não encontrado."
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "dbt-env" ]; then
    echo "🔄 Ativando ambiente virtual..."
    source dbt-env/bin/activate
fi

# Navegar para o diretório do dbt
cd DGU

echo "📋 PASSO 1: Verificar configuração..."
dbt debug --profiles-dir .

echo ""
echo "🌱 PASSO 2: Carregar seeds..."
dbt seed --profiles-dir .

echo ""
echo "🧪 PASSO 3: Testar modelo staging simples..."
dbt run --profiles-dir . --select stg_test_simple

echo ""
echo "🧪 PASSO 4: Testar modelo mart simples..."
dbt run --profiles-dir . --select mart_test_simple

echo ""
echo "🔄 PASSO 5: Executar staging completo..."
dbt run --profiles-dir . --select staging

echo ""
echo "📈 PASSO 6: Executar mart completo..."
dbt run --profiles-dir . --select mart

echo ""
echo "✅ Teste concluído!"
