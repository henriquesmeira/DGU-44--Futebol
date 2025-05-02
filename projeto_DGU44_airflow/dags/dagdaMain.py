from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='executar_pipeline_completo',
    start_date=datetime(2025, 5, 2),
    schedule_interval='0 8 * * 2,5',
    catchup=False,
    tags=['pipeline', 'completo', 'bigquery'],
) as dag:
    executar_main = BashOperator(
        task_id='executar_script_main',
        bash_command='python /opt/airflow/dags/main.py',
    )