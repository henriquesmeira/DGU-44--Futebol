import pandas as pd

def extrair_tabelas_selecionadas(url, nome_time, indice_tabelas):
    tabelas = pd.read_html(url)
    return {f"{nome_time}_tabela_{i}": tabelas[i] for i in indice_tabelas}

def extrair_dados():
    indice_desejados = [0, 1, 4, 5, 6, 10]
    times_urls = {
        "palmeiras": 'https://fbref.com/en/squads/abdce579/Palmeiras-Stats',
        "flamengo": 'https://fbref.com/en/squads/639950ae/Flamengo-Stats',
        "corinthians": 'https://fbref.com/en/squads/bf4acd28/Corinthians-Stats',
        "sao_paulo": 'https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats',
        "internacional": 'https://fbref.com/en/squads/6f7e1f03/Internacional-Stats'
    }

    dataframes = {}
    for nome, url in times_urls.items():
        dataframes.update(extrair_tabelas_selecionadas(url, nome, indice_desejados))
    return dataframes







