from extract import extrair_dados, valor_mercado
from load import enviar_para_bigquery
import logging

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

if __name__ == "__main__":
    logger.info("Iniciando extração de dados de estatísticas de futebol...")
    
    # Extrai dados do fbref.com
    dataframes_stats = extrair_dados()
    logger.info(f"Extraídos {len(dataframes_stats)} dataframes de estatísticas")
    
    # Extrai dados de valor de mercado do transfermarkt.com
    dataframes_mercado = valor_mercado()
    logger.info(f"Extraídos {len(dataframes_mercado)} dataframes de valor de mercado")
    
    # Combina todos os dataframes
    todos_dataframes = {**dataframes_stats, **dataframes_mercado}
    logger.info(f"Total de {len(todos_dataframes)} dataframes para envio ao BigQuery")
    
    # Envia para o BigQuery
    enviar_para_bigquery(todos_dataframes, project_id, dataset_id)
    logger.info("Processo concluído com sucesso!")