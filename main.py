from extract import extrair_dados
from load import enviar_para_bigquery

project_id = "dataglowup-458411"
dataset_id = "DataGlowUp"

if __name__ == "__main__":
    dataframes = extrair_dados()
    enviar_para_bigquery(dataframes, project_id, dataset_id)
