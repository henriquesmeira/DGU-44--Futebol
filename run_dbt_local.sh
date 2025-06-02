#!/bin/bash

# Script para executar dbt usando profiles.yml local
echo "=== EXECUTANDO DBT COM PROFILES LOCAL ==="
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

echo "📋 1. Testando configuração com profiles local..."
dbt debug --profiles-dir .

echo ""
echo "📊 2. Listando modelos com profiles local..."
dbt list --profiles-dir . --resource-type model

echo ""
echo "🌱 3. Carregando seeds..."
dbt seed --profiles-dir .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Seeds carregados com sucesso!"
    echo ""
    echo "🔄 4. Executando modelos staging..."
    dbt run --profiles-dir . --select staging
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Staging executado com sucesso!"
        echo ""
        echo "📈 5. Executando modelos mart..."
        dbt run --profiles-dir . --select mart
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 SUCESSO! Todas as camadas foram criadas!"
            echo ""
            echo "📊 Verificando no BigQuery:"
            echo "   • Dataset DataGlowUp (seeds)"
            echo "   • Dataset DataGlowUp_staging (views)"
            echo "   • Dataset DataGlowUp_mart (tabelas)"
        else
            echo ""
            echo "❌ Erro ao executar modelos mart"
        fi
    else
        echo ""
        echo "❌ Erro ao executar modelos staging"
    fi
else
    echo ""
    echo "❌ Erro ao carregar seeds"
fi
