"""
DAG do Apache Airflow para orquestrar o pipeline de dados de futebol DGU.

Executa extração de dados dos sites de futebol e processamento via dbt
nas terças e sextas-feiras às 09:00 (horário de Brasília).
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.sensors.bigquery import BigQueryTableExistenceSensor
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append('/opt/airflow/project')

# Importar funções do projeto DGU
from extract import extrair_dados, valor_mercado
from main import salvar_como_seeds

# Configurações padrão da DAG
default_args = {
    'owner': 'dgu-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1, tzinfo=None),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Definição da DAG
dag = DAG(
    'dgu_futebol_pipeline',
    default_args=default_args,
    description='Pipeline de dados de futebol DGU - Extração e processamento',
    schedule_interval='0 9 * * 2,5',  # Terças e sextas às 09:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['dgu', 'futebol', 'bigquery', 'dbt'],
)

def extrair_dados_futebol(**context):
    """Extrai dados de estatísticas dos times de futebol."""
    try:
        print("🔍 Iniciando extração de dados de estatísticas...")
        dataframes_stats = extrair_dados()
        
        # Salvar dados no contexto para próximas tasks
        context['task_instance'].xcom_push(
            key='dataframes_stats', 
            value=len(dataframes_stats)
        )
        
        print(f"✅ {len(dataframes_stats)} dataframes de estatísticas extraídos")
        return dataframes_stats
        
    except Exception as e:
        print(f"❌ Erro na extração de estatísticas: {str(e)}")
        raise

def extrair_valores_mercado(**context):
    """Extrai dados de valores de mercado dos jogadores."""
    try:
        print("💰 Iniciando extração de valores de mercado...")
        dataframes_mercado = valor_mercado()
        
        # Salvar dados no contexto para próximas tasks
        context['task_instance'].xcom_push(
            key='dataframes_mercado', 
            value=len(dataframes_mercado)
        )
        
        print(f"✅ {len(dataframes_mercado)} dataframes de valor de mercado extraídos")
        return dataframes_mercado
        
    except Exception as e:
        print(f"❌ Erro na extração de valores de mercado: {str(e)}")
        raise

def processar_e_salvar_seeds(**context):
    """Processa e salva os dados extraídos como seeds do dbt."""
    try:
        print("💾 Processando e salvando dados como seeds...")
        
        # Recuperar dados das tasks anteriores
        ti = context['task_instance']
        
        # Re-executar extrações para obter os dados
        dataframes_stats = extrair_dados()
        dataframes_mercado = valor_mercado()
        
        # Combinar todos os dataframes
        todos_dataframes = {**dataframes_stats, **dataframes_mercado}
        
        # Salvar como seeds
        salvar_como_seeds(todos_dataframes)
        
        print(f"✅ {len(todos_dataframes)} dataframes salvos como seeds")
        
        # Salvar informações no XCom
        context['task_instance'].xcom_push(
            key='total_dataframes', 
            value=len(todos_dataframes)
        )
        
        return len(todos_dataframes)
        
    except Exception as e:
        print(f"❌ Erro ao processar e salvar seeds: {str(e)}")
        raise

def verificar_dados_extraidos(**context):
    """Verifica se os dados foram extraídos corretamente."""
    try:
        ti = context['task_instance']
        total_dataframes = ti.xcom_pull(key='total_dataframes', task_ids='processar_seeds')
        
        if total_dataframes and total_dataframes > 0:
            print(f"✅ Verificação OK: {total_dataframes} dataframes processados")
            return True
        else:
            raise ValueError("Nenhum dataframe foi processado")
            
    except Exception as e:
        print(f"❌ Erro na verificação dos dados: {str(e)}")
        raise

# Task 1: Extração de dados de estatísticas
task_extrair_stats = PythonOperator(
    task_id='extrair_estatisticas',
    python_callable=extrair_dados_futebol,
    dag=dag,
)

# Task 2: Extração de valores de mercado
task_extrair_mercado = PythonOperator(
    task_id='extrair_valores_mercado',
    python_callable=extrair_valores_mercado,
    dag=dag,
)

# Task 3: Processar e salvar seeds
task_processar_seeds = PythonOperator(
    task_id='processar_seeds',
    python_callable=processar_e_salvar_seeds,
    dag=dag,
)

# Task 4: Verificar dados extraídos
task_verificar_dados = PythonOperator(
    task_id='verificar_dados_extraidos',
    python_callable=verificar_dados_extraidos,
    dag=dag,
)

# Task Group para dbt
with TaskGroup('dbt_pipeline', dag=dag) as dbt_group:
    
    # Task 5: Carregar seeds no BigQuery
    task_dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/dbt && dbt seed --profiles-dir .',
        dag=dag,
    )
    
    # Task 6: Executar modelos staging
    task_dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /opt/airflow/dbt && dbt run --select staging --profiles-dir .',
        dag=dag,
    )
    
    # Task 7: Executar modelos mart
    task_dbt_mart = BashOperator(
        task_id='dbt_run_mart',
        bash_command='cd /opt/airflow/dbt && dbt run --select mart --profiles-dir .',
        dag=dag,
    )
    
    # Task 8: Executar testes dbt
    task_dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
        dag=dag,
    )
    
    # Definir dependências dentro do grupo dbt
    task_dbt_seed >> task_dbt_staging >> task_dbt_mart >> task_dbt_test

# Task 9: Verificar tabelas criadas no BigQuery
task_verificar_bigquery = BigQueryCheckOperator(
    task_id='verificar_tabelas_bigquery',
    sql="""
    SELECT COUNT(*) as total_tables
    FROM `dataglowup-458411.DataGlowUp_mart.INFORMATION_SCHEMA.TABLES`
    WHERE table_name IN ('mart_players_stats', 'mart_players_market_value', 'mart_teams_summary')
    """,
    use_legacy_sql=False,
    gcp_conn_id='google_cloud_default',
    dag=dag,
)

# Task 10: Notificação de sucesso
def notificar_sucesso(**context):
    """Notifica o sucesso da execução do pipeline."""
    execution_date = context['execution_date']
    print(f"🎉 Pipeline DGU executado com sucesso em {execution_date}")
    print("📊 Dados de futebol atualizados no BigQuery!")
    
    # Aqui você pode adicionar notificações por email, Slack, etc.
    return "Pipeline executado com sucesso!"

task_notificar_sucesso = PythonOperator(
    task_id='notificar_sucesso',
    python_callable=notificar_sucesso,
    dag=dag,
)

# Definir dependências das tasks
[task_extrair_stats, task_extrair_mercado] >> task_processar_seeds
task_processar_seeds >> task_verificar_dados >> dbt_group
dbt_group >> task_verificar_bigquery >> task_notificar_sucesso
