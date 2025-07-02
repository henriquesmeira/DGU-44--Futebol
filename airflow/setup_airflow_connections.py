"""
Script para configurar conexões e variáveis do Airflow para o projeto DGU.
Execute este script após inicializar o Airflow.
"""

import os
from airflow.models import Connection, Variable
from airflow.utils.db import create_session
from airflow.configuration import conf

def setup_bigquery_connection():
    """Configura a conexão com o BigQuery."""
    
    # Configuração da conexão BigQuery
    bigquery_conn = Connection(
        conn_id='google_cloud_default',
        conn_type='google_cloud_platform',
        description='Conexão BigQuery para projeto DGU',
        extra={
            'extra__google_cloud_platform__project': 'dataglowup-458411',
            'extra__google_cloud_platform__key_path': '/opt/airflow/credentials/bigquery-credentials.json',
            'extra__google_cloud_platform__scope': 'https://www.googleapis.com/auth/cloud-platform',
            'extra__google_cloud_platform__num_retries': 5,
        }
    )
    
    with create_session() as session:
        # Verificar se conexão já existe
        existing_conn = session.query(Connection).filter(
            Connection.conn_id == 'google_cloud_default'
        ).first()
        
        if existing_conn:
            print("🔄 Atualizando conexão BigQuery existente...")
            existing_conn.conn_type = bigquery_conn.conn_type
            existing_conn.description = bigquery_conn.description
            existing_conn.extra = bigquery_conn.extra
        else:
            print("➕ Criando nova conexão BigQuery...")
            session.add(bigquery_conn)
        
        session.commit()
        print("✅ Conexão BigQuery configurada com sucesso!")

def setup_variables():
    """Configura variáveis do Airflow para o projeto DGU."""
    
    variables = {
        # Configurações do projeto
        'dgu_project_id': 'dataglowup-458411',
        'dgu_dataset_main': 'DataGlowUp',
        'dgu_dataset_staging': 'DataGlowUp_staging',
        'dgu_dataset_mart': 'DataGlowUp_mart',
        
        # Configurações de execução
        'dgu_max_retries': '3',
        'dgu_timeout_minutes': '120',
        'dgu_email_alerts': 'admin@dgu.com',
        
        # URLs dos sites (para facilitar manutenção)
        'dgu_url_palmeiras_stats': 'https://fbref.com/en/squads/abdce579/Palmeiras-Stats',
        'dgu_url_flamengo_stats': 'https://fbref.com/en/squads/639950ae/Flamengo-Stats',
        'dgu_url_corinthians_stats': 'https://fbref.com/en/squads/bf4acd28/Corinthians-Stats',
        
        'dgu_url_palmeiras_market': 'https://www.transfermarkt.com/palmeiras/startseite/verein/614',
        'dgu_url_flamengo_market': 'https://www.transfermarkt.com/flamengo-rio-de-janeiro/startseite/verein/614',
        'dgu_url_corinthians_market': 'https://www.transfermarkt.com/corinthians-sao-paulo/startseite/verein/614',
        
        # Configurações de monitoramento
        'dgu_data_freshness_hours': '96',  # 4 dias
        'dgu_min_players_per_team': '15',
        'dgu_max_players_per_team': '50',
        
        # Configurações de notificação
        'dgu_slack_webhook': '',  # Adicionar webhook do Slack se necessário
        'dgu_teams_webhook': '',  # Adicionar webhook do Teams se necessário
    }
    
    for key, value in variables.items():
        try:
            Variable.set(key, value, description=f'Variável DGU: {key}')
            print(f"✅ Variável {key} configurada")
        except Exception as e:
            print(f"❌ Erro ao configurar variável {key}: {e}")
    
    print(f"✅ {len(variables)} variáveis configuradas com sucesso!")

def setup_pools():
    """Configura pools de recursos do Airflow."""
    from airflow.models import Pool
    
    pools = [
        {
            'pool': 'dgu_extraction_pool',
            'slots': 2,
            'description': 'Pool para tasks de extração de dados'
        },
        {
            'pool': 'dgu_bigquery_pool',
            'slots': 3,
            'description': 'Pool para operações no BigQuery'
        },
        {
            'pool': 'dgu_dbt_pool',
            'slots': 1,
            'description': 'Pool para execução do dbt'
        }
    ]
    
    with create_session() as session:
        for pool_config in pools:
            existing_pool = session.query(Pool).filter(
                Pool.pool == pool_config['pool']
            ).first()
            
            if existing_pool:
                print(f"🔄 Atualizando pool {pool_config['pool']}...")
                existing_pool.slots = pool_config['slots']
                existing_pool.description = pool_config['description']
            else:
                print(f"➕ Criando pool {pool_config['pool']}...")
                new_pool = Pool(
                    pool=pool_config['pool'],
                    slots=pool_config['slots'],
                    description=pool_config['description']
                )
                session.add(new_pool)
        
        session.commit()
        print("✅ Pools configurados com sucesso!")

def verify_setup():
    """Verifica se a configuração foi realizada corretamente."""
    print("\n🔍 Verificando configuração...")
    
    # Verificar conexão BigQuery
    with create_session() as session:
        bigquery_conn = session.query(Connection).filter(
            Connection.conn_id == 'google_cloud_default'
        ).first()
        
        if bigquery_conn:
            print("✅ Conexão BigQuery encontrada")
        else:
            print("❌ Conexão BigQuery não encontrada")
    
    # Verificar algumas variáveis importantes
    important_vars = ['dgu_project_id', 'dgu_dataset_main', 'dgu_max_retries']
    
    for var_name in important_vars:
        try:
            value = Variable.get(var_name)
            print(f"✅ Variável {var_name}: {value}")
        except Exception:
            print(f"❌ Variável {var_name} não encontrada")
    
    # Verificar arquivo de credenciais
    credentials_path = '/opt/airflow/credentials/bigquery-credentials.json'
    if os.path.exists(credentials_path):
        print("✅ Arquivo de credenciais encontrado")
    else:
        print("❌ Arquivo de credenciais não encontrado")
    
    print("\n🎯 Configuração concluída!")

def main():
    """Função principal para executar toda a configuração."""
    print("🚀 Iniciando configuração do Airflow para projeto DGU...")
    print("=" * 60)
    
    try:
        setup_bigquery_connection()
        setup_variables()
        setup_pools()
        verify_setup()
        
        print("\n🎉 Configuração do Airflow concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Verificar se as credenciais BigQuery estão no local correto")
        print("2. Acessar a interface web do Airflow em http://localhost:8080")
        print("3. Ativar as DAGs 'dgu_futebol_pipeline' e 'dgu_monitoring'")
        print("4. Testar execução manual das DAGs")
        
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        raise

if __name__ == "__main__":
    main()
