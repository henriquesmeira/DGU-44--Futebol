"""
DAG para executar o pipeline completo de extração e carregamento de dados de futebol.
Esta DAG segue as boas práticas do Airflow, usando PythonOperator em vez de BashOperator
para executar código Python.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from utils.extract import extrair_dados
from utils.load import enviar_para_bigquery

# Configurações do projeto
PROJECT_ID = "dataglowup-458411"
DATASET_ID = "DataGlowUp"

def executar_pipeline(**kwargs):
    """
    Função principal que executa o pipeline completo de extração e carregamento.
    
    Esta função é chamada pelo PythonOperator e executa todo o processo de ETL.
    """
    print("Iniciando o processo de extração de dados...")
    dataframes = extrair_dados()
    print(f"Extração concluída. {len(dataframes)} tabelas extraídas.")
    
    print(f"Iniciando o carregamento para o BigQuery (Projeto: {PROJECT_ID}, Dataset: {DATASET_ID})...")
    enviar_para_bigquery(dataframes, PROJECT_ID, DATASET_ID)
    print("Pipeline concluído com sucesso!")
    
    return "Pipeline executado com sucesso"

# Definição da DAG
with DAG(
    dag_id='executar_pipeline_completo_v2',  # Nova versão da DAG
    description='Pipeline ETL para dados de futebol usando boas práticas',
    start_date=datetime(2025, 5, 2),
    schedule_interval='0 8 * * 2,5',  # Às 8h nas terças e sextas
    catchup=False,
    tags=['pipeline', 'completo', 'bigquery', 'futebol'],
) as dag:
    
    # Tarefa única que executa todo o pipeline
    executar_task = PythonOperator(
        task_id='executar_pipeline',
        python_callable=executar_pipeline,
        provide_context=True,
        doc_md="""
        ### Tarefa de Execução do Pipeline
        
        Esta tarefa executa o pipeline completo de ETL:
        1. Extrai dados de estatísticas de futebol de várias equipes
        2. Carrega os dados no BigQuery
        
        Os dados são extraídos do site fbref.com e carregados no dataset DataGlowUp.
        """,
    )
    
    # Se quiser dividir em múltiplas tarefas no futuro, pode fazer assim:
    # extrair_task = PythonOperator(...)
    # carregar_task = PythonOperator(...)
    # extrair_task >> carregar_task
