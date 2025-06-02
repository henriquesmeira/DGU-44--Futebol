import os
import subprocess
import sys
import logging
import pandas as pd
from extract import extrair_dados, valor_mercado

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main_execution.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

project_id = "dataglowup-458411"
dataset_id = "DataGlowUp"

def salvar_como_seeds(dataframes):
    """Salva os dataframes extraídos como arquivos CSV na pasta seeds do dbt."""
    seeds_dir = "DGU/seeds"

    logger.info("💾 Salvando dados extraídos como seeds do dbt...")

    for nome_tabela, df in dataframes.items():
        # Limpar o dataframe para compatibilidade com CSV
        df_clean = df.copy()

        # Converter datetime para string
        for col in df_clean.columns:
            if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)

        # Salvar como CSV
        arquivo_csv = f"{seeds_dir}/{nome_tabela}.csv"
        df_clean.to_csv(arquivo_csv, index=False)
        logger.info(f"   ✅ {arquivo_csv} salvo com {len(df_clean)} registros")

def executar_dbt():
    """Executa o pipeline dbt completo."""
    logger.info("🏗️ Executando pipeline dbt...")

    # Mudar para o diretório do dbt
    os.chdir("DGU")

    try:
        # 1. Carregar seeds
        logger.info("🌱 Carregando seeds no BigQuery...")
        subprocess.run(
            ["dbt", "seed", "--profiles-dir", "."],
            capture_output=True, text=True, check=True
        )
        logger.info("   ✅ Seeds carregados com sucesso!")

        # 2. Executar modelos staging
        logger.info("🔄 Executando modelos staging...")
        subprocess.run(
            ["dbt", "run", "--profiles-dir", ".", "--select", "staging"],
            capture_output=True, text=True, check=True
        )
        logger.info("   ✅ Staging executado com sucesso!")

        # 3. Executar modelos mart
        logger.info("📈 Executando modelos mart...")
        subprocess.run(
            ["dbt", "run", "--profiles-dir", ".", "--select", "mart"],
            capture_output=True, text=True, check=True
        )
        logger.info("   ✅ Mart executado com sucesso!")

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao executar dbt: {e}")
        logger.error(f"Saída do erro: {e.stderr}")
        return False
    finally:
        # Voltar para o diretório raiz
        os.chdir("..")

if __name__ == "__main__":
    logger.info("🚀 INICIANDO PIPELINE COMPLETO DGU - DADOS DE FUTEBOL")
    logger.info("=" * 60)

    try:
        # ETAPA 1: Extração de dados reais
        logger.info("📊 ETAPA 1: Extraindo dados reais dos sites...")

        # Extrai dados do fbref.com
        logger.info("   🔍 Extraindo estatísticas do fbref.com...")
        dataframes_stats = extrair_dados()
        logger.info(f"   ✅ {len(dataframes_stats)} dataframes de estatísticas extraídos")

        # Extrai dados de valor de mercado do transfermarkt.com
        logger.info("   💰 Extraindo valores de mercado do transfermarkt.com...")
        dataframes_mercado = valor_mercado()
        logger.info(f"   ✅ {len(dataframes_mercado)} dataframes de valor de mercado extraídos")

        # Combina todos os dataframes
        todos_dataframes = {**dataframes_stats, **dataframes_mercado}
        logger.info(f"   📋 Total: {len(todos_dataframes)} dataframes extraídos")

        # ETAPA 2: Salvar como seeds
        logger.info("\n💾 ETAPA 2: Salvando dados como seeds do dbt...")
        salvar_como_seeds(todos_dataframes)

        # ETAPA 3: Executar pipeline dbt
        logger.info("\n🏗️ ETAPA 3: Executando pipeline dbt...")
        sucesso_dbt = executar_dbt()

        if sucesso_dbt:
            logger.info("\n🎉 PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
            logger.info("=" * 60)
            logger.info("📊 ESTRUTURA CRIADA NO BIGQUERY:")
            logger.info("")
            logger.info("📁 Dataset DataGlowUp (dados brutos):")
            logger.info("   • palmeiras_tabela_0, flamengo_tabela_0, corinthians_tabela_0")
            logger.info("   • palmeiras_tabela_0_mercado, flamengo_tabela_0_mercado, corinthians_tabela_0_mercado")
            logger.info("")
            logger.info("🔄 Dataset DataGlowUp_staging (views limpas):")
            logger.info("   • stg_*_stats, stg_*_market (6 views)")
            logger.info("")
            logger.info("📈 Dataset DataGlowUp_mart (tabelas finais):")
            logger.info("   • mart_players_stats (todos os jogadores)")
            logger.info("   • mart_players_market_value (valores de mercado)")
            logger.info("   • mart_teams_summary (resumo por time)")
            logger.info("")
            logger.info("🎯 Acesse o BigQuery Console para analisar os dados!")
        else:
            logger.error("❌ Erro na execução do pipeline dbt")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Erro no pipeline: {str(e)}")
        sys.exit(1)