#!/bin/bash

# Script para executar o pipeline completo com correções
echo "=== PIPELINE COMPLETO DBT - CORRIGIDO ==="
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

if [ $? -ne 0 ]; then
    echo "❌ Erro na configuração do dbt"
    exit 1
fi

echo ""
echo "🌱 PASSO 2: Carregar seeds no BigQuery..."
dbt seed --profiles-dir .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao carregar seeds"
    exit 1
fi

echo ""
echo "✅ Seeds carregados com sucesso!"
echo ""
echo "🧪 PASSO 3: Testar modelo simples..."
dbt run --profiles-dir . --select stg_test_simple

if [ $? -eq 0 ]; then
    echo "✅ Modelo de teste funcionou!"
else
    echo "❌ Modelo de teste falhou"
fi

echo ""
echo "🔄 PASSO 4: Executar todos os modelos staging..."
dbt run --profiles-dir . --select staging

if [ $? -eq 0 ]; then
    echo "✅ Staging executado com sucesso!"
    
    echo ""
    echo "📈 PASSO 5: Executar todos os modelos mart..."
    dbt run --profiles-dir . --select mart
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCESSO TOTAL! Pipeline completo executado!"
        echo ""
        echo "📊 Estrutura criada no BigQuery:"
        echo "   📁 Dataset DataGlowUp:"
        echo "      • palmeiras_tabela_0"
        echo "      • flamengo_tabela_0"
        echo "      • corinthians_tabela_0"
        echo "      • palmeiras_tabela_0_mercado"
        echo "      • flamengo_tabela_0_mercado"
        echo "      • corinthians_tabela_0_mercado"
        echo ""
        echo "   🔄 Dataset DataGlowUp_staging:"
        echo "      • stg_palmeiras_stats (view)"
        echo "      • stg_flamengo_stats (view)"
        echo "      • stg_corinthians_stats (view)"
        echo "      • stg_palmeiras_market (view)"
        echo "      • stg_flamengo_market (view)"
        echo "      • stg_corinthians_market (view)"
        echo ""
        echo "   📈 Dataset DataGlowUp_mart:"
        echo "      • mart_players_stats (tabela)"
        echo "      • mart_players_market_value (tabela)"
        echo "      • mart_teams_summary (tabela)"
        echo ""
        echo "🎯 Acesse o BigQuery Console para ver as tabelas!"
    else
        echo "❌ Erro ao executar modelos mart"
        exit 1
    fi
else
    echo "❌ Erro ao executar modelos staging"
    exit 1
fi
