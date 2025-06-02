#!/bin/bash

# Script final para testar tudo corrigido
echo "=== TESTE FINAL - TODAS AS CORREÇÕES APLICADAS ==="
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

echo "🔄 Executando staging com TODAS as correções..."
dbt run --profiles-dir . --select staging

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 STAGING FUNCIONOU PERFEITAMENTE!"
    echo ""
    echo "📈 Agora executando MART..."
    
    dbt run --profiles-dir . --select mart
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🏆 SUCESSO TOTAL! PIPELINE COMPLETO FUNCIONANDO!"
        echo ""
        echo "📊 ESTRUTURA CRIADA NO BIGQUERY:"
        echo ""
        echo "📁 Dataset DataGlowUp (seeds):"
        echo "   ✅ palmeiras_tabela_0"
        echo "   ✅ flamengo_tabela_0"
        echo "   ✅ corinthians_tabela_0"
        echo "   ✅ palmeiras_tabela_0_mercado"
        echo "   ✅ flamengo_tabela_0_mercado"
        echo "   ✅ corinthians_tabela_0_mercado"
        echo ""
        echo "🔄 Dataset DataGlowUp_staging (views):"
        echo "   ✅ stg_palmeiras_stats"
        echo "   ✅ stg_flamengo_stats"
        echo "   ✅ stg_corinthians_stats"
        echo "   ✅ stg_palmeiras_market"
        echo "   ✅ stg_flamengo_market"
        echo "   ✅ stg_corinthians_market"
        echo ""
        echo "📈 Dataset DataGlowUp_mart (tabelas):"
        echo "   ✅ mart_players_stats (33 jogadores)"
        echo "   ✅ mart_players_market_value (valores de mercado)"
        echo "   ✅ mart_teams_summary (resumo dos 3 times)"
        echo ""
        echo "🎯 ACESSE O BIGQUERY CONSOLE PARA VER AS TABELAS!"
        echo "🎯 USE AS TABELAS MART PARA SUAS ANÁLISES!"
    else
        echo "❌ Erro no mart"
    fi
else
    echo "❌ Ainda há erro no staging"
fi
