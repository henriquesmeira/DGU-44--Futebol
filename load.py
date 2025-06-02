import os
import pandas as pd
import logging
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pandas_gbq import to_gbq

# Configuração de logging
logger = logging.getLogger("load")

# Caminho das credenciais
caminho_credenciais = r"/home/dadosdmxcapital/Área de trabalho/Novo Projeto DGU/dataglowup-458411-7384de8e6f21.json"
if not os.path.exists(caminho_credenciais):
    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {caminho_credenciais}")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = caminho_credenciais

def verificar_ou_criar_dataset(cliente, project_id, dataset_id):
    """Verifica se um dataset existe e cria se necessário."""
    try:
        cliente.get_dataset(dataset_id)
        logger.info(f"Dataset {dataset_id} já existe.")
    except NotFound:
        logger.info(f"Dataset {dataset_id} não encontrado. Criando...")
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"  # Definindo localização explicitamente
        cliente.create_dataset(dataset)
        logger.info(f"Dataset {dataset_id} criado com sucesso.")

def deletar_tabela_se_existir(cliente, dataset_id, nome_tabela):
    """Deleta uma tabela se ela existir."""
    tabela_id = f"{cliente.project}.{dataset_id}.{nome_tabela}"
    try:
        cliente.delete_table(tabela_id)
        logger.info(f"Tabela {tabela_id} excluída com sucesso.")
    except NotFound:
        logger.info(f"Tabela {tabela_id} não encontrada. Nada para excluir.")

def inferir_schema_dataframe(df):
    """Infere o schema do dataframe para o BigQuery."""
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
    return schema

def verificar_dataframe(df, nome_tabela):
    """Verifica se o dataframe está pronto para ser enviado ao BigQuery."""
    # Verificar colunas vazias
    colunas_vazias = df.columns[df.isna().all()].tolist()
    if colunas_vazias:
        logger.warning(f"Tabela {nome_tabela} possui colunas completamente vazias: {colunas_vazias}")
    
    # Verificar tipos de dados inconsistentes
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # Verificar se poderia ser numérico
                pd.to_numeric(df[col], errors='raise')
                logger.warning(f"Coluna {col} em {nome_tabela} poderia ser convertida para numérico")
            except:
                pass
    
    return df

def enviar_para_bigquery(dataframes, project_id, dataset_id, tables_to_delete_always=None):
    """Envia os dataframes para o BigQuery.
    
    Args:
        dataframes (dict): Dicionário de dataframes a serem enviados.
        project_id (str): ID do projeto BigQuery.
        dataset_id (str): ID do dataset BigQuery.
        tables_to_delete_always (list, optional): Lista de nomes de tabelas a serem
            excluídas antes de qualquer carregamento. Defaults to None.
    """
    cliente = bigquery.Client(project=project_id)
    verificar_ou_criar_dataset(cliente, project_id, dataset_id)
    
    # Excluir tabelas especificadas para exclusão permanente
    if tables_to_delete_always:
        logger.info(f"Iniciando exclusão de tabelas especificadas: {tables_to_delete_always}")
        for old_table_name in tables_to_delete_always:
            deletar_tabela_se_existir(cliente, dataset_id, old_table_name)
        logger.info("Exclusão de tabelas especificadas concluída.")

    resultados = {"sucesso": [], "falha": []}
    
    for nome_tabela, df in dataframes.items():
        # Verificar e preparar o dataframe
        df = verificar_dataframe(df, nome_tabela)
        
        # A lógica de exclusão para tabelas que estão sendo carregadas já está
        # implícita no `write_disposition="WRITE_TRUNCATE"` ou `if_exists='replace'`.
        logger.info(f"Iniciando envio para {dataset_id}.{nome_tabela}...")
        
        try:
            # Tentativa com o método padrão
            config_job = bigquery.LoadJobConfig(
                autodetect=True, 
                write_disposition="WRITE_TRUNCATE" # Isso irá truncar/substituir se a tabela existir
            )
            ref_tabela = f"{project_id}.{dataset_id}.{nome_tabela}"
            job = cliente.load_table_from_dataframe(df, ref_tabela, job_config=config_job)
            job.result()  # Aguarda conclusão
            tabela = cliente.get_table(ref_tabela)
            logger.info(f"✔ {tabela.num_rows} linhas carregadas em {ref_tabela}")
            resultados["sucesso"].append(nome_tabela)
            
        except Exception as e:
            logger.error(f"❌ Falha no método tradicional para {nome_tabela}: {str(e)}")
            logger.info("Tentando método alternativo...")
            
            try:
                # Método alternativo usando pandas_gbq com schema explícito
                schema = inferir_schema_dataframe(df)
                to_gbq(
                    df, 
                    f"{dataset_id}.{nome_tabela}", 
                    project_id=project_id, 
                    if_exists='replace', # Isso irá substituir se a tabela existir
                    table_schema=schema
                )
                logger.info(f"✔ {nome_tabela} carregado com sucesso via método alternativo!")
                resultados["sucesso"].append(nome_tabela)
                
            except Exception as e:
                logger.error(f"❌ Falha também no método alternativo para {nome_tabela}: {str(e)}")
                resultados["falha"].append(nome_tabela)
    
    # Resumo dos resultados
    logger.info(f"Resumo do envio: {len(resultados['sucesso'])} tabelas enviadas com sucesso, {len(resultados['falha'])} falhas")
    if resultados["falha"]:
        logger.error(f"Tabelas com falha: {resultados['falha']}")
    
    return resultados
