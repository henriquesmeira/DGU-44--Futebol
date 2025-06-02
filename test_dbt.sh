#!/bin/bash

# Script para testar o dbt e identificar problemas
echo "=== Teste de Configuração DBT ==="
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

echo "📋 Testando configuração do dbt..."
dbt debug

echo ""
echo "📊 Listando modelos disponíveis..."
dbt list

echo ""
echo "🔍 Compilando modelos (sem executar)..."
dbt compile

echo ""
echo "📈 Testando dependências dos modelos..."
dbt deps

echo ""
echo "✅ Teste concluído. Verifique os logs acima para identificar problemas."
