import pandas as pd
import requests
from datetime import datetime
import logging
from io import StringIO # Importar StringIO para lidar com FutureWarning

# Configuração de logging
logger = logging.getLogger("extract")

def extrair_tabelas_selecionadas(url, nome_time, indice_tabelas):
    """Extrai tabelas específicas de uma URL com tratamento de erro."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Tentativa de acesso com tratamento de erro e timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Usar StringIO para silenciar FutureWarning e garantir que pd.read_html
        # trate a string como um objeto de arquivo
        tabelas = pd.read_html(StringIO(response.text)) 
        
        # Criação dos dataframes com limpeza e informações adicionais
        resultado = {}
        for i in indice_tabelas:
            if i < len(tabelas):
                df = tabelas[i]
                
                # --- CORREÇÃO 1: Lidar com MultiIndex em colunas ---
                # Se as colunas forem um MultiIndex, achata-as.
                if isinstance(df.columns, pd.MultiIndex):
                    # Junta os níveis do MultiIndex com um underscore
                    df.columns = ['_'.join(col).strip() for col in df.columns.values]
                
                # Limpeza de colunas (melhorada para lidar com '/')
                # Adicionado .replace('/', '_') para compatibilidade com BigQuery
                df.columns = [
                    col.strip()
                       .replace(' ', '_')
                       .replace('.', '_')
                       .replace('-', '_')
                       .replace('/', '_') # Adicionado para lidar com barras
                       .lower() 
                    for col in df.columns
                ]
                
                # Limpeza de valores monetários/percentuais
                for col in df.select_dtypes(include=['object']).columns:
                    try:
                        # Adicionado .astype(str) para robustez ao lidar com tipos mistos
                        if df[col].astype(str).str.contains('R\$|\$|€|%', na=False).any():
                            df[col] = df[col].astype(str).str.replace('R\$|\$|€|%', '', regex=True)
                            df[col] = df[col].str.replace('.', '', regex=False)  # Remove separador de milhar
                            df[col] = df[col].str.replace(',', '.', regex=False)  # Converte vírgula para ponto decimal
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    except Exception as err:
                        logger.warning(f"Erro ao limpar coluna {col}: {err}")
                
                # Adiciona metadados
                df['time'] = nome_time
                df['data_extracao'] = datetime.now()
                df['fonte'] = url
                
                resultado[f"{nome_time}_tabela_{i}"] = df
        
        return resultado
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao aceder {url}: {e}")
        return {}
    except ValueError as e:
        logger.error(f"Não foi possível encontrar tabelas em {url}: {e}")
        return {}
    except Exception as e:
        # Captura o tipo de erro para melhor depuração
        logger.error(f"Erro desconhecido ao processar {url}: {type(e).__name__}: {e}")
        return {}

def extrair_dados():
    """Extrai dados das estatísticas dos times do fbref.com."""
    indice_desejados = [0]
    times_urls = {
        "palmeiras": 'https://fbref.com/en/squads/abdce579/Palmeiras-Stats',
        "flamengo": 'https://fbref.com/en/squads/639950ae/Flamengo-Stats',
        "corinthians": 'https://fbref.com/en/squads/bf4acd28/Corinthians-Stats'
    }

    dataframes = {}
    for nome, url in times_urls.items():
        logger.info(f"A extrair estatísticas de {nome} em {url}")
        df_time = extrair_tabelas_selecionadas(url, nome, indice_desejados)
        if df_time:
            dataframes.update(df_time)
        else:
            logger.warning(f"Nenhum dado extraído para {nome}")
    
    return dataframes

def valor_mercado():
    """Extrai dados de valor de mercado do transfermarkt.com."""
    indice_desejado = [0]
    urls_times = {
        "corinthians": 'https://www.transfermarkt.com.br/sc-corinthians/kader/verein/199/saison_id/2024/plus/1',
        "palmeiras": 'https://www.transfermarkt.com.br/se-palmeiras/kader/verein/1023/saison_id/2024/plus/1',
        "flamengo": 'https://www.transfermarkt.com.br/cr-flamengo/kader/verein/614/saison_id/2024/plus/1'
    }

    dataframes = {}
    for nome, url in urls_times.items():
        logger.info(f"A extrair valor de mercado de {nome} em {url}")
        df_mercado = extrair_tabelas_selecionadas(url, nome, indice_desejado)
        if df_mercado:
            # Renomeando para diferenciar das tabelas de estatísticas
            dataframes.update({f"{k}_mercado": v for k, v in df_mercado.items()})
        else:
            logger.warning(f"Nenhum dado de valor de mercado extraído para {nome}")
    
    return dataframes