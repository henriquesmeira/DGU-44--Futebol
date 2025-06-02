#!/bin/bash

# Script para carregar os seeds do dbt no BigQuery
# Projeto DGU - Dados de Futebol

echo "=== Carregamento dos Seeds do DBT - Projeto DGU ==="
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "DGU" ]; then
    echo "❌ Erro: Diretório DGU não encontrado. Execute este script na raiz do projeto."
    exit 1
fi

# Verificar se o arquivo de credenciais existe
if [ ! -f "dataglowup-458411-7384de8e6f21.json" ]; then
    echo "❌ Erro: Arquivo de credenciais não encontrado: dataglowup-458411-7384de8e6f21.json"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "dbt-env" ]; then
    echo "🔄 Ativando ambiente virtual..."
    source dbt-env/bin/activate
fi

# Navegar para o diretório do dbt
cd DGU

echo "📋 Verificando configuração do dbt..."
dbt debug

if [ $? -ne 0 ]; then
    echo "❌ Erro na configuração do dbt. Verifique o arquivo profiles.yml"
    exit 1
fi

echo ""
echo "📊 Carregando seeds no BigQuery..."
echo ""

# Carregar todos os seeds
dbt seed

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Seeds carregados com sucesso!"
    echo ""
    echo "🏗️ Executando modelos dbt (staging e mart)..."
    echo ""

    # Executar todos os modelos
    dbt run

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Pipeline dbt executado com sucesso!"
        echo ""
        echo "📈 Estrutura criada no BigQuery:"
        echo ""
        echo "📁 Seeds (dataset principal):"
        echo "   • palmeiras_tabela_0"
        echo "   • flamengo_tabela_0"
        echo "   • corinthians_tabela_0"
        echo "   • palmeiras_tabela_0_mercado"
        echo "   • flamengo_tabela_0_mercado"
        echo "   • corinthians_tabela_0_mercado"
        echo ""
        echo "🔄 Staging Views (dataset staging):"
        echo "   • stg_palmeiras_stats"
        echo "   • stg_flamengo_stats"
        echo "   • stg_corinthians_stats"
        echo "   • stg_palmeiras_market"
        echo "   • stg_flamengo_market"
        echo "   • stg_corinthians_market"
        echo ""
        echo "📊 Mart Tables (dataset mart):"
        echo "   • mart_players_stats (todos os jogadores)"
        echo "   • mart_players_market_value (valores de mercado)"
        echo "   • mart_teams_summary (resumo por time)"
        echo ""
        echo "🎯 Próximos passos:"
        echo "   1. Acesse o BigQuery Console"
        echo "   2. Navegue pelos datasets: DataGlowUp, DataGlowUp_staging, DataGlowUp_mart"
        echo "   3. Use as tabelas mart para análises finais"
        echo "   4. Execute consultas SQL nas tabelas mart para insights"
    else
        echo ""
        echo "❌ Erro ao executar modelos dbt. Verifique os logs acima."
        exit 1
    fi
else
    echo ""
    echo "❌ Erro ao carregar seeds. Verifique os logs acima."
    exit 1
fi
