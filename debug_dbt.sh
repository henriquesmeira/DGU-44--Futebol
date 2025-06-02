#!/bin/bash

# Script para diagnosticar problemas do dbt
echo "=== DIAGNÓSTICO COMPLETO DBT ==="
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

echo "📋 1. Testando configuração básica..."
dbt debug

echo ""
echo "📊 2. Listando todos os recursos..."
dbt list --resource-type all

echo ""
echo "🔍 3. Verificando apenas modelos..."
dbt list --resource-type model

echo ""
echo "🌱 4. Verificando seeds..."
dbt list --resource-type seed

echo ""
echo "📝 5. Compilando modelos (verificar sintaxe)..."
dbt compile

echo ""
echo "🎯 6. Tentando executar apenas staging..."
dbt run --select staging

echo ""
echo "📈 7. Tentando executar apenas mart..."
dbt run --select mart

echo ""
echo "🔧 8. Verificando estrutura de arquivos..."
echo "Modelos staging:"
ls -la models/staging/

echo ""
echo "Modelos mart:"
ls -la models/mart/

echo ""
echo "Seeds:"
ls -la seeds/

echo ""
echo "✅ Diagnóstico concluído!"
