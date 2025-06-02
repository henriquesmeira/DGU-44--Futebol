#!/bin/bash

# Script para testar apenas staging após correções
echo "=== TESTE STAGING CORRIGIDO ==="
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

echo "🔄 Executando modelos staging corrigidos..."
dbt run --profiles-dir . --select staging

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ STAGING FUNCIONOU! Agora executando MART..."
    echo ""
    
    dbt run --profiles-dir . --select mart
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCESSO TOTAL! Pipeline completo funcionando!"
        echo ""
        echo "📊 Verifique no BigQuery:"
        echo "   • DataGlowUp_staging (6 views)"
        echo "   • DataGlowUp_mart (3 tabelas)"
    else
        echo "❌ Erro no mart, mas staging funcionou!"
    fi
else
    echo "❌ Ainda há erro no staging"
fi
