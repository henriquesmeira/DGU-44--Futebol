import os
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pandas_gbq import to_gbq
from extract import extrair_dados

# Caminho das credenciais
caminho_credenciais = r"C:\Users\henrique.soares\Desktop\Futebol\dataglowup-458411-4a4b4b3a4f14.json"
if not os.path.exists(caminho_credenciais):
    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {caminho_credenciais}")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = caminho_credenciais

project_id = "dataglowup-458411"
dataset_id = "DataGlowUp"

def verificar_ou_criar_dataset(cliente, project_id, dataset_id):
    try:
        cliente.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} já existe.")
    except NotFound:
        print(f"Dataset {dataset_id} não encontrado. Criando...")
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        cliente.create_dataset(dataset)
        print(f"Dataset {dataset_id} criado com sucesso.")

def enviar_para_bigquery(dataframes, project_id, dataset_id):
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

if __name__ == "__main__":
    dataframes = extrair_dados()
    enviar_para_bigquery(dataframes, project_id, dataset_id)
