"""
Operadores customizados do Airflow para o projeto DGU.
"""

import os
import sys
import subprocess
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from airflow.exceptions import AirflowException
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

# Adicionar projeto ao path
sys.path.append('/opt/airflow/project')

class DGUExtractionOperator(BaseOperator):
    """
    Operador customizado para extração de dados de futebol.
    """
    
    template_fields = ['teams', 'extraction_type']
    
    @apply_defaults
    def __init__(
        self,
        extraction_type: str = 'stats',  # 'stats' ou 'market'
        teams: Optional[List[str]] = None,
        timeout: int = 300,
        retries: int = 2,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.extraction_type = extraction_type
        self.teams = teams or ['palmeiras', 'flamengo', 'corinthians']
        self.timeout = timeout
        self.retries = retries
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Executa a extração de dados."""
        
        try:
            if self.extraction_type == 'stats':
                from extract import extrair_dados
                self.log.info("🔍 Iniciando extração de estatísticas...")
                dataframes = extrair_dados()
                
            elif self.extraction_type == 'market':
                from extract import valor_mercado
                self.log.info("💰 Iniciando extração de valores de mercado...")
                dataframes = valor_mercado()
                
            else:
                raise AirflowException(f"Tipo de extração inválido: {self.extraction_type}")
            
            # Validar resultados
            if not dataframes:
                raise AirflowException("Nenhum dataframe foi extraído")
            
            self.log.info(f"✅ {len(dataframes)} dataframes extraídos com sucesso")
            
            # Salvar informações no XCom
            extraction_info = {
                'extraction_type': self.extraction_type,
                'dataframes_count': len(dataframes),
                'teams_processed': list(dataframes.keys()),
                'extraction_time': datetime.now().isoformat()
            }
            
            context['task_instance'].xcom_push(
                key=f'extraction_info_{self.extraction_type}',
                value=extraction_info
            )
            
            return extraction_info
            
        except Exception as e:
            self.log.error(f"❌ Erro na extração {self.extraction_type}: {str(e)}")
            raise AirflowException(f"Falha na extração: {str(e)}")

class DGUSeedsOperator(BaseOperator):
    """
    Operador customizado para processar e salvar seeds do dbt.
    """
    
    @apply_defaults
    def __init__(
        self,
        seeds_directory: str = '/opt/airflow/dbt/seeds',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.seeds_directory = seeds_directory
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Processa e salva os dados como seeds."""
        
        try:
            # Importar funções necessárias
            from extract import extrair_dados, valor_mercado
            from main import salvar_como_seeds
            
            self.log.info("💾 Processando dados para seeds...")
            
            # Extrair dados
            dataframes_stats = extrair_dados()
            dataframes_mercado = valor_mercado()
            
            # Combinar dataframes
            todos_dataframes = {**dataframes_stats, **dataframes_mercado}
            
            if not todos_dataframes:
                raise AirflowException("Nenhum dataframe disponível para salvar como seeds")
            
            # Salvar como seeds
            salvar_como_seeds(todos_dataframes)
            
            self.log.info(f"✅ {len(todos_dataframes)} seeds salvos com sucesso")
            
            # Informações para XCom
            seeds_info = {
                'seeds_count': len(todos_dataframes),
                'seeds_names': list(todos_dataframes.keys()),
                'seeds_directory': self.seeds_directory,
                'processing_time': datetime.now().isoformat()
            }
            
            context['task_instance'].xcom_push(key='seeds_info', value=seeds_info)
            
            return seeds_info
            
        except Exception as e:
            self.log.error(f"❌ Erro ao processar seeds: {str(e)}")
            raise AirflowException(f"Falha no processamento de seeds: {str(e)}")

class DGUDbtOperator(BaseOperator):
    """
    Operador customizado para executar comandos dbt.
    """
    
    template_fields = ['dbt_command', 'profiles_dir', 'select']
    
    @apply_defaults
    def __init__(
        self,
        dbt_command: str,
        profiles_dir: str = '/opt/airflow/dbt',
        select: Optional[str] = None,
        exclude: Optional[str] = None,
        vars: Optional[Dict[str, Any]] = None,
        timeout: int = 1800,  # 30 minutos
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.dbt_command = dbt_command
        self.profiles_dir = profiles_dir
        self.select = select
        self.exclude = exclude
        self.vars = vars or {}
        self.timeout = timeout
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Executa comando dbt."""
        
        try:
            # Construir comando dbt
            cmd = ['dbt', self.dbt_command, '--profiles-dir', self.profiles_dir]
            
            if self.select:
                cmd.extend(['--select', self.select])
            
            if self.exclude:
                cmd.extend(['--exclude', self.exclude])
            
            if self.vars:
                vars_str = ' '.join([f'{k}={v}' for k, v in self.vars.items()])
                cmd.extend(['--vars', vars_str])
            
            self.log.info(f"🔧 Executando: {' '.join(cmd)}")
            
            # Executar comando
            result = subprocess.run(
                cmd,
                cwd=self.profiles_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Log da saída
            if result.stdout:
                self.log.info(f"📋 Saída dbt:\n{result.stdout}")
            
            if result.stderr:
                self.log.warning(f"⚠️ Avisos dbt:\n{result.stderr}")
            
            # Verificar se comando foi bem-sucedido
            if result.returncode != 0:
                raise AirflowException(f"Comando dbt falhou com código {result.returncode}")
            
            self.log.info(f"✅ Comando dbt '{self.dbt_command}' executado com sucesso")
            
            # Informações para XCom
            dbt_info = {
                'command': self.dbt_command,
                'return_code': result.returncode,
                'execution_time': datetime.now().isoformat(),
                'select': self.select,
                'exclude': self.exclude
            }
            
            context['task_instance'].xcom_push(key='dbt_info', value=dbt_info)
            
            return dbt_info
            
        except subprocess.TimeoutExpired:
            self.log.error(f"❌ Timeout na execução do dbt após {self.timeout} segundos")
            raise AirflowException(f"Timeout na execução do dbt")
        
        except Exception as e:
            self.log.error(f"❌ Erro na execução do dbt: {str(e)}")
            raise AirflowException(f"Falha na execução do dbt: {str(e)}")

class DGUDataQualityOperator(BaseOperator):
    """
    Operador customizado para verificações de qualidade de dados.
    """
    
    @apply_defaults
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_name: str,
        quality_checks: List[Dict[str, Any]],
        gcp_conn_id: str = 'google_cloud_default',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_name = table_name
        self.quality_checks = quality_checks
        self.gcp_conn_id = gcp_conn_id
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Executa verificações de qualidade."""
        
        try:
            # Conectar ao BigQuery
            hook = BigQueryHook(gcp_conn_id=self.gcp_conn_id)
            
            self.log.info(f"🔍 Executando verificações de qualidade para {self.table_name}")
            
            results = []
            
            for check in self.quality_checks:
                check_name = check.get('name', 'Verificação sem nome')
                sql = check.get('sql', '')
                expected_result = check.get('expected_result')
                
                self.log.info(f"   Executando: {check_name}")
                
                # Executar query
                query_result = hook.get_pandas_df(sql)
                
                if len(query_result) == 0:
                    raise AirflowException(f"Query de qualidade '{check_name}' não retornou resultados")
                
                actual_result = query_result.iloc[0, 0]
                
                # Verificar resultado
                if expected_result is not None:
                    if actual_result != expected_result:
                        results.append({
                            'check': check_name,
                            'status': 'FALHA',
                            'expected': expected_result,
                            'actual': actual_result
                        })
                        self.log.error(f"   ❌ {check_name}: Esperado {expected_result}, obtido {actual_result}")
                    else:
                        results.append({
                            'check': check_name,
                            'status': 'OK',
                            'expected': expected_result,
                            'actual': actual_result
                        })
                        self.log.info(f"   ✅ {check_name}: OK")
                else:
                    results.append({
                        'check': check_name,
                        'status': 'INFO',
                        'actual': actual_result
                    })
                    self.log.info(f"   ℹ️ {check_name}: {actual_result}")
            
            # Verificar se houve falhas
            falhas = [r for r in results if r['status'] == 'FALHA']
            if falhas:
                raise AirflowException(f"Verificações de qualidade falharam: {len(falhas)} de {len(results)}")
            
            self.log.info(f"✅ Todas as verificações de qualidade passaram ({len(results)} checks)")
            
            # Salvar resultados no XCom
            quality_info = {
                'table': f"{self.project_id}.{self.dataset_id}.{self.table_name}",
                'checks_total': len(results),
                'checks_passed': len([r for r in results if r['status'] == 'OK']),
                'checks_failed': len(falhas),
                'results': results,
                'execution_time': datetime.now().isoformat()
            }
            
            context['task_instance'].xcom_push(key='quality_info', value=quality_info)
            
            return quality_info
            
        except Exception as e:
            self.log.error(f"❌ Erro nas verificações de qualidade: {str(e)}")
            raise AirflowException(f"Falha nas verificações de qualidade: {str(e)}")
