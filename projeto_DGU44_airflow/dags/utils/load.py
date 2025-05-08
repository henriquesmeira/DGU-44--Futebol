import os
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pandas_gbq import to_gbq

def verificar_ou_criar_dataset(cliente, project_id, dataset_id):
    """
    Verifica se um dataset existe no BigQuery e o cria se não existir.

    Args:
        cliente: Cliente BigQuery
        project_id (str): ID do projeto GCP
        dataset_id (str): ID do dataset a ser verificado/criado
    """
    try:
        cliente.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} já existe.")
    except NotFound:
        print(f"Dataset {dataset_id} não encontrado. Criando...")
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        cliente.create_dataset(dataset)
        print(f"Dataset {dataset_id} criado com sucesso.")

def enviar_para_bigquery(dataframes, project_id, dataset_id):
    """
    Envia dataframes para o BigQuery.

    Args:
        dataframes (dict): Dicionário de dataframes para enviar
        project_id (str): ID do projeto GCP
        dataset_id (str): ID do dataset onde as tabelas serão criadas
    """
    # Configurar o caminho para o arquivo de credenciais
    # No ambiente Docker, o arquivo está mapeado para /keys/
    credentials_path = "/keys/credenciais-gcp.json"

    # Verificar se o arquivo existe
    if not os.path.exists(credentials_path):
        print(f"AVISO: Arquivo de credenciais não encontrado em {credentials_path}")
        print("Tentando usar credenciais padrão do ambiente...")
    else:
        print(f"Usando arquivo de credenciais: {credentials_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    # Criar o cliente BigQuery
    cliente = bigquery.Client(project=project_id)
    verificar_ou_criar_dataset(cliente, project_id, dataset_id)

    for nome_tabela, df in dataframes.items():
        print(f"Iniciando envio para {dataset_id}.{nome_tabela}...")
        try:
            config_job = bigquery.LoadJobConfig(autodetect=True, write_disposition="WRITE_TRUNCATE")
            ref_tabela = f"{project_id}.{dataset_id}.{nome_tabela}"
            job = cliente.load_table_from_dataframe(df, ref_tabela, job_config=config_job)
            job.result()
            tabela = cliente.get_table(ref_tabela)
            print(f"✔ {tabela.num_rows} linhas carregadas em {ref_tabela}")
        except Exception as e:
            print(f"❌ Falha no método tradicional para {nome_tabela}: {str(e)}")
            print("Tentando método alternativo...")
            try:
                schema = []
                for col_name, dtype in df.dtypes.items():
                    if pd.api.types.is_integer_dtype(dtype):
                        schema.append({"name": str(col_name), "type": "INTEGER"})
                    elif pd.api.types.is_float_dtype(dtype):
                        schema.append({"name": str(col_name), "type": "FLOAT"})
                    elif pd.api.types.is_datetime64_dtype(dtype):
                        schema.append({"name": str(col_name), "type": "TIMESTAMP"})
                    elif pd.api.types.is_bool_dtype(dtype):
                        schema.append({"name": str(col_name), "type": "BOOLEAN"})
                    else:
                        schema.append({"name": str(col_name), "type": "STRING"})
                to_gbq(df, f"{dataset_id}.{nome_tabela}", project_id=project_id, if_exists='replace', table_schema=schema)
                print(f"✔ {nome_tabela} carregado com sucesso via método alternativo!")
            except Exception as e:
                print(f"❌ Falha também no método alternativo para {nome_tabela}: {str(e)}")
