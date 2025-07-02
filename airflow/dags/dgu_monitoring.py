"""
DAG de monitoramento para o pipeline DGU de dados de futebol.

Executa verificações de qualidade de dados e monitoramento diário.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryValueCheckOperator
from airflow.utils.task_group import TaskGroup

# Configurações padrão
default_args = {
    'owner': 'dgu-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# DAG de monitoramento
dag = DAG(
    'dgu_monitoring',
    default_args=default_args,
    description='Monitoramento e verificações de qualidade dos dados DGU',
    schedule_interval='0 10 * * *',  # Diariamente às 10:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['dgu', 'monitoring', 'quality'],
)

def verificar_atualizacao_dados(**context):
    """Verifica se os dados foram atualizados recentemente."""
    from google.cloud import bigquery
    
    client = bigquery.Client()
    
    # Verificar última atualização das tabelas mart
    query = """
    SELECT 
        table_name,
        TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), last_modified_time, HOUR) as horas_desde_atualizacao
    FROM `dataglowup-458411.DataGlowUp_mart.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'mart_%'
    ORDER BY last_modified_time DESC
    """
    
    results = client.query(query).to_dataframe()
    
    for _, row in results.iterrows():
        table_name = row['table_name']
        horas = row['horas_desde_atualizacao']
        
        print(f"📊 Tabela {table_name}: atualizada há {horas} horas")
        
        # Alertar se dados estão muito antigos (mais de 4 dias)
        if horas > 96:  # 4 dias
            print(f"⚠️ ALERTA: Tabela {table_name} não foi atualizada há {horas} horas!")
    
    return results.to_dict('records')

def verificar_qualidade_dados(**context):
    """Executa verificações de qualidade nos dados."""
    from google.cloud import bigquery
    
    client = bigquery.Client()
    
    verificacoes = []
    
    # 1. Verificar se há dados duplicados
    query_duplicados = """
    SELECT 
        'mart_players_stats' as tabela,
        COUNT(*) as total_registros,
        COUNT(DISTINCT CONCAT(player, time)) as registros_unicos
    FROM `dataglowup-458411.DataGlowUp_mart.mart_players_stats`
    """
    
    result = client.query(query_duplicados).to_dataframe()
    total = result.iloc[0]['total_registros']
    unicos = result.iloc[0]['registros_unicos']
    
    if total != unicos:
        verificacoes.append({
            'tipo': 'DUPLICADOS',
            'status': 'FALHA',
            'detalhes': f'Encontrados {total - unicos} registros duplicados'
        })
    else:
        verificacoes.append({
            'tipo': 'DUPLICADOS',
            'status': 'OK',
            'detalhes': 'Nenhum registro duplicado encontrado'
        })
    
    # 2. Verificar valores nulos em campos críticos
    query_nulos = """
    SELECT 
        COUNT(*) as total,
        COUNTIF(player IS NULL) as player_nulo,
        COUNTIF(time IS NULL) as time_nulo
    FROM `dataglowup-458411.DataGlowUp_mart.mart_players_stats`
    """
    
    result = client.query(query_nulos).to_dataframe()
    player_nulo = result.iloc[0]['player_nulo']
    time_nulo = result.iloc[0]['time_nulo']
    
    if player_nulo > 0 or time_nulo > 0:
        verificacoes.append({
            'tipo': 'VALORES_NULOS',
            'status': 'FALHA',
            'detalhes': f'Player nulo: {player_nulo}, Time nulo: {time_nulo}'
        })
    else:
        verificacoes.append({
            'tipo': 'VALORES_NULOS',
            'status': 'OK',
            'detalhes': 'Nenhum valor nulo em campos críticos'
        })
    
    # Imprimir resultados
    for verificacao in verificacoes:
        status_emoji = "✅" if verificacao['status'] == 'OK' else "❌"
        print(f"{status_emoji} {verificacao['tipo']}: {verificacao['detalhes']}")
    
    return verificacoes

def gerar_relatorio_diario(**context):
    """Gera relatório diário do pipeline."""
    from google.cloud import bigquery
    
    client = bigquery.Client()
    
    # Estatísticas gerais
    query_stats = """
    SELECT 
        COUNT(DISTINCT time) as total_times,
        COUNT(*) as total_jogadores,
        AVG(gls) as media_gols,
        MAX(data_extracao) as ultima_extracao
    FROM `dataglowup-458411.DataGlowUp_mart.mart_players_stats`
    """
    
    stats = client.query(query_stats).to_dataframe().iloc[0]
    
    relatorio = f"""
    📊 RELATÓRIO DIÁRIO DGU - {datetime.now().strftime('%d/%m/%Y')}
    ================================================
    
    📈 Estatísticas Gerais:
    • Times monitorados: {stats['total_times']}
    • Total de jogadores: {stats['total_jogadores']}
    • Média de gols por jogador: {stats['media_gols']:.2f}
    • Última extração: {stats['ultima_extracao']}
    
    🔍 Verificações de Qualidade:
    """
    
    # Adicionar verificações de qualidade
    verificacoes = verificar_qualidade_dados()
    for v in verificacoes:
        status_emoji = "✅" if v['status'] == 'OK' else "❌"
        relatorio += f"    {status_emoji} {v['tipo']}: {v['detalhes']}\n"
    
    print(relatorio)
    
    # Salvar relatório no XCom
    context['task_instance'].xcom_push(key='relatorio_diario', value=relatorio)
    
    return relatorio

# Task Group para verificações de qualidade
with TaskGroup('verificacoes_qualidade', dag=dag) as quality_group:
    
    # Verificar se tabelas existem
    task_check_tables = BigQueryCheckOperator(
        task_id='verificar_existencia_tabelas',
        sql="""
        SELECT COUNT(*) as total
        FROM `dataglowup-458411.DataGlowUp_mart.INFORMATION_SCHEMA.TABLES`
        WHERE table_name IN ('mart_players_stats', 'mart_players_market_value', 'mart_teams_summary')
        """,
        use_legacy_sql=False,
        gcp_conn_id='google_cloud_default',
    )
    
    # Verificar se há dados nas tabelas
    task_check_data = BigQueryValueCheckOperator(
        task_id='verificar_dados_tabelas',
        sql="""
        SELECT COUNT(*) 
        FROM `dataglowup-458411.DataGlowUp_mart.mart_players_stats`
        """,
        pass_value=0,
        use_legacy_sql=False,
        gcp_conn_id='google_cloud_default',
    )
    
    task_check_tables >> task_check_data

# Tasks de monitoramento
task_verificar_atualizacao = PythonOperator(
    task_id='verificar_atualizacao_dados',
    python_callable=verificar_atualizacao_dados,
    dag=dag,
)

task_verificar_qualidade = PythonOperator(
    task_id='verificar_qualidade_dados',
    python_callable=verificar_qualidade_dados,
    dag=dag,
)

task_relatorio_diario = PythonOperator(
    task_id='gerar_relatorio_diario',
    python_callable=gerar_relatorio_diario,
    dag=dag,
)

# Definir dependências
quality_group >> task_verificar_atualizacao >> task_verificar_qualidade >> task_relatorio_diario
