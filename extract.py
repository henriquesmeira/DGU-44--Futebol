import pandas as pd
import requests
from datetime import datetime
import logging
from io import StringIO

# Configuração de logging
logger = logging.getLogger("extract")

def extrair_tabelas_selecionadas(url, nome_time, indice_tabelas):
    """
    Extrai tabelas específicas de uma URL usando requests e pandas.read_html.
    Esta função é adequada para páginas com conteúdo estático (não gerado por JS).
    Inclui lógica aprimorada para limpeza de valores monetários com 'M'/'K'.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Tentativa de acesso com tratamento de erro e timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        
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
                
                # Limpeza de valores monetários/percentuais e outros textos
                for col in df.select_dtypes(include=['object']).columns:
                    try:
                        original_values = df[col].astype(str)
                        
                        # Verifica se a coluna contém símbolos de moeda OU 'M'/'K'
                        # Esta condição torna a limpeza específica para valores de mercado ou números formatados de forma similar
                        if original_values.str.contains(r'R\$|\$|€|%|M|K', na=False).any():
                            cleaned_values = original_values.str.replace(r'R\$|\$|€|%', '', regex=True).str.strip()

                            def _convert_market_value_internal(val):
                                if pd.isna(val) or str(val).strip().lower() == 'none': # Lida com NaN real ou string 'None'
                                    return val
                                val_str = str(val).strip()
                                if 'M' in val_str:
                                    num_str = val_str.replace('M', '').strip().replace(',', '.')
                                    try:
                                        return float(num_str) * 1_000_000
                                    except ValueError:
                                        return val_str # Retorna como string se a conversão falhar
                                elif 'K' in val_str:
                                    num_str = val_str.replace('K', '').strip().replace(',', '.')
                                    try:
                                        return float(num_str) * 1_000
                                    except ValueError:
                                        return val_str # Retorna como string se a conversão falhar
                                else:
                                    # Para valores sem 'M' ou 'K', tenta a conversão direta
                                    # Remove o ponto como separador de milhar e substitui vírgula por ponto decimal
                                    num_str = val_str.replace('.', '', regex=False).replace(',', '.', regex=False)
                                    try:
                                        return float(num_str)
                                    except ValueError:
                                        return val_str # Retorna como string se a conversão falhar
                            
                            df[col] = cleaned_values.apply(_convert_market_value_internal)
                        else:
                            # Para outras colunas de objeto que não possuem moeda/M/K,
                            # tenta uma conversão numérica geral (se aplicável)
                            temp_col = original_values.str.replace('.', '', regex=False) # Remove separadores de milhar
                            temp_col = temp_col.str.replace(',', '.', regex=False) # Converte vírgula decimal para ponto
                            df[col] = pd.to_numeric(temp_col, errors='coerce')

                    except Exception as err:
                        logger.warning(f"Erro ao limpar e converter coluna {col}: {err}")
                
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
    """Extrai dados de valor de mercado do ogol.com.br usando requests e pandas.read_html."""
    indice_desejado = [0] # Geralmente a primeira tabela é a de jogadores
    urls_times = {
        "corinthians": 'https://www.ogol.com.br/equipe/corinthians/valor-de-mercado',
        "palmeiras": 'https://www.ogol.com.br/equipe/palmeiras/valor-de-mercado',
        "flamengo": 'https://www.ogol.com.br/equipe/flamengo/valor-de-mercado'
    }

    dataframes = {}
    for nome, url in urls_times.items():
        logger.info(f"A extrair valor de mercado de {nome} em {url}")
        # Chama a função baseada em requests (extrair_tabelas_selecionadas)
        df_mercado = extrair_tabelas_selecionadas(url, nome, indice_desejado)
        if df_mercado:
            # Renomeando para diferenciar das tabelas de estatísticas
            dataframes.update({f"{k}_mercado": v for k, v in df_mercado.items()})
        else:
            logger.warning(f"Nenhum dado de valor de mercado extraído para {nome}")
    
    return dataframes
