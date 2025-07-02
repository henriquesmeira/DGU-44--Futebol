"""
Sistema de alertas e monitoramento para o projeto DGU.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from airflow.models import BaseOperator, Variable
from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from airflow.exceptions import AirflowException
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

class DGUAlertOperator(BaseOperator):
    """
    Operador para envio de alertas do pipeline DGU.
    """
    
    @apply_defaults
    def __init__(
        self,
        alert_type: str = 'success',  # 'success', 'failure', 'warning'
        message: str = '',
        include_stats: bool = True,
        channels: List[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.alert_type = alert_type
        self.message = message
        self.include_stats = include_stats
        self.channels = channels or ['log']  # 'log', 'slack', 'teams', 'email'
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Envia alertas configurados."""
        
        try:
            # Preparar informações do contexto
            dag_id = context['dag'].dag_id
            task_id = context['task'].task_id
            execution_date = context['execution_date']
            
            # Construir mensagem base
            base_message = self._build_base_message(dag_id, task_id, execution_date)
            
            if self.message:
                full_message = f"{base_message}\n\n{self.message}"
            else:
                full_message = base_message
            
            # Adicionar estatísticas se solicitado
            if self.include_stats:
                stats = self._get_pipeline_stats(context)
                if stats:
                    full_message += f"\n\n📊 Estatísticas:\n{stats}"
            
            # Enviar para cada canal configurado
            results = {}
            for channel in self.channels:
                try:
                    if channel == 'log':
                        self._send_log_alert(full_message)
                        results[channel] = 'success'
                    elif channel == 'slack':
                        self._send_slack_alert(full_message)
                        results[channel] = 'success'
                    elif channel == 'teams':
                        self._send_teams_alert(full_message)
                        results[channel] = 'success'
                    elif channel == 'email':
                        self._send_email_alert(full_message, context)
                        results[channel] = 'success'
                    else:
                        self.log.warning(f"Canal de alerta desconhecido: {channel}")
                        results[channel] = 'unknown_channel'
                        
                except Exception as e:
                    self.log.error(f"Erro ao enviar alerta para {channel}: {str(e)}")
                    results[channel] = f'error: {str(e)}'
            
            alert_info = {
                'alert_type': self.alert_type,
                'channels': self.channels,
                'results': results,
                'message_length': len(full_message),
                'timestamp': datetime.now().isoformat()
            }
            
            return alert_info
            
        except Exception as e:
            self.log.error(f"❌ Erro no sistema de alertas: {str(e)}")
            raise AirflowException(f"Falha no sistema de alertas: {str(e)}")
    
    def _build_base_message(self, dag_id: str, task_id: str, execution_date: datetime) -> str:
        """Constrói mensagem base do alerta."""
        
        emoji_map = {
            'success': '✅',
            'failure': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        emoji = emoji_map.get(self.alert_type, '📋')
        
        message = f"{emoji} **DGU Pipeline Alert**\n"
        message += f"**Tipo:** {self.alert_type.upper()}\n"
        message += f"**DAG:** {dag_id}\n"
        message += f"**Task:** {task_id}\n"
        message += f"**Execução:** {execution_date.strftime('%d/%m/%Y %H:%M:%S')}\n"
        
        return message
    
    def _get_pipeline_stats(self, context: Context) -> Optional[str]:
        """Obtém estatísticas do pipeline."""
        
        try:
            # Tentar obter informações do XCom
            ti = context['task_instance']
            
            # Buscar informações de extração
            extraction_stats = ti.xcom_pull(key='extraction_info_stats')
            market_stats = ti.xcom_pull(key='extraction_info_market')
            seeds_info = ti.xcom_pull(key='seeds_info')
            
            stats_lines = []
            
            if extraction_stats:
                stats_lines.append(f"• Estatísticas extraídas: {extraction_stats.get('dataframes_count', 0)} dataframes")
            
            if market_stats:
                stats_lines.append(f"• Valores de mercado extraídos: {market_stats.get('dataframes_count', 0)} dataframes")
            
            if seeds_info:
                stats_lines.append(f"• Seeds processados: {seeds_info.get('seeds_count', 0)} arquivos")
            
            # Adicionar estatísticas do BigQuery se disponível
            try:
                bq_stats = self._get_bigquery_stats()
                if bq_stats:
                    stats_lines.extend(bq_stats)
            except Exception:
                pass  # Ignorar erros de BigQuery
            
            return '\n'.join(stats_lines) if stats_lines else None
            
        except Exception as e:
            self.log.warning(f"Erro ao obter estatísticas: {str(e)}")
            return None
    
    def _get_bigquery_stats(self) -> List[str]:
        """Obtém estatísticas do BigQuery."""
        
        try:
            hook = BigQueryHook(gcp_conn_id='google_cloud_default')
            
            # Query para contar registros nas tabelas mart
            query = """
            SELECT 
                table_name,
                row_count
            FROM `dataglowup-458411.DataGlowUp_mart.__TABLES__`
            WHERE table_name LIKE 'mart_%'
            """
            
            result = hook.get_pandas_df(query)
            
            stats = []
            for _, row in result.iterrows():
                stats.append(f"• {row['table_name']}: {row['row_count']} registros")
            
            return stats
            
        except Exception:
            return []
    
    def _send_log_alert(self, message: str):
        """Envia alerta para o log."""
        
        if self.alert_type == 'success':
            self.log.info(f"🎉 ALERTA SUCESSO:\n{message}")
        elif self.alert_type == 'failure':
            self.log.error(f"💥 ALERTA FALHA:\n{message}")
        elif self.alert_type == 'warning':
            self.log.warning(f"⚠️ ALERTA AVISO:\n{message}")
        else:
            self.log.info(f"📋 ALERTA INFO:\n{message}")
    
    def _send_slack_alert(self, message: str):
        """Envia alerta para o Slack."""
        
        try:
            webhook_url = Variable.get('dgu_slack_webhook', default_var=None)
            
            if not webhook_url:
                self.log.warning("Webhook do Slack não configurado")
                return
            
            color_map = {
                'success': 'good',
                'failure': 'danger',
                'warning': 'warning',
                'info': '#36a64f'
            }
            
            payload = {
                'text': 'DGU Pipeline Alert',
                'attachments': [{
                    'color': color_map.get(self.alert_type, '#36a64f'),
                    'text': message,
                    'footer': 'DGU Monitoring System',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.log.info("✅ Alerta enviado para Slack")
            
        except Exception as e:
            self.log.error(f"Erro ao enviar alerta para Slack: {str(e)}")
            raise
    
    def _send_teams_alert(self, message: str):
        """Envia alerta para o Microsoft Teams."""
        
        try:
            webhook_url = Variable.get('dgu_teams_webhook', default_var=None)
            
            if not webhook_url:
                self.log.warning("Webhook do Teams não configurado")
                return
            
            color_map = {
                'success': '00FF00',
                'failure': 'FF0000',
                'warning': 'FFA500',
                'info': '0078D4'
            }
            
            payload = {
                '@type': 'MessageCard',
                '@context': 'https://schema.org/extensions',
                'summary': 'DGU Pipeline Alert',
                'themeColor': color_map.get(self.alert_type, '0078D4'),
                'sections': [{
                    'activityTitle': 'DGU Pipeline Alert',
                    'activitySubtitle': f'Tipo: {self.alert_type.upper()}',
                    'text': message,
                    'markdown': True
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.log.info("✅ Alerta enviado para Teams")
            
        except Exception as e:
            self.log.error(f"Erro ao enviar alerta para Teams: {str(e)}")
            raise
    
    def _send_email_alert(self, message: str, context: Context):
        """Envia alerta por email."""
        
        try:
            from airflow.utils.email import send_email
            
            email_to = Variable.get('dgu_email_alerts', default_var=None)
            
            if not email_to:
                self.log.warning("Email de alertas não configurado")
                return
            
            subject = f"DGU Pipeline Alert - {self.alert_type.upper()}"
            
            # Converter para HTML
            html_message = message.replace('\n', '<br>')
            html_message = html_message.replace('**', '<strong>').replace('**', '</strong>')
            
            send_email(
                to=[email_to],
                subject=subject,
                html_content=f"<html><body><pre>{html_message}</pre></body></html>"
            )
            
            self.log.info("✅ Alerta enviado por email")
            
        except Exception as e:
            self.log.error(f"Erro ao enviar alerta por email: {str(e)}")
            raise

class DGUHealthCheckOperator(BaseOperator):
    """
    Operador para verificações de saúde do sistema.
    """
    
    @apply_defaults
    def __init__(
        self,
        checks: List[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.checks = checks or ['bigquery', 'data_freshness', 'data_quality']
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Executa verificações de saúde."""
        
        results = {}
        
        for check in self.checks:
            try:
                if check == 'bigquery':
                    results[check] = self._check_bigquery_connection()
                elif check == 'data_freshness':
                    results[check] = self._check_data_freshness()
                elif check == 'data_quality':
                    results[check] = self._check_data_quality()
                else:
                    results[check] = {'status': 'unknown', 'message': f'Verificação desconhecida: {check}'}
                    
            except Exception as e:
                results[check] = {'status': 'error', 'message': str(e)}
        
        # Verificar se há falhas críticas
        critical_failures = [k for k, v in results.items() if v.get('status') == 'error']
        
        if critical_failures:
            self.log.error(f"❌ Verificações de saúde falharam: {critical_failures}")
        else:
            self.log.info("✅ Todas as verificações de saúde passaram")
        
        return results
    
    def _check_bigquery_connection(self) -> Dict[str, Any]:
        """Verifica conexão com BigQuery."""
        
        try:
            hook = BigQueryHook(gcp_conn_id='google_cloud_default')
            
            # Teste simples de conexão
            query = "SELECT 1 as test"
            result = hook.get_pandas_df(query)
            
            if len(result) == 1 and result.iloc[0, 0] == 1:
                return {'status': 'ok', 'message': 'Conexão BigQuery OK'}
            else:
                return {'status': 'error', 'message': 'Resposta inesperada do BigQuery'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Erro na conexão BigQuery: {str(e)}'}
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Verifica se os dados estão atualizados."""
        
        try:
            hook = BigQueryHook(gcp_conn_id='google_cloud_default')
            
            # Verificar última atualização
            query = """
            SELECT 
                MAX(last_modified_time) as ultima_atualizacao
            FROM `dataglowup-458411.DataGlowUp_mart.INFORMATION_SCHEMA.TABLES`
            WHERE table_name LIKE 'mart_%'
            """
            
            result = hook.get_pandas_df(query)
            ultima_atualizacao = result.iloc[0, 0]
            
            # Calcular diferença em horas
            agora = datetime.now()
            diff_hours = (agora - ultima_atualizacao).total_seconds() / 3600
            
            max_hours = int(Variable.get('dgu_data_freshness_hours', default_var='96'))
            
            if diff_hours <= max_hours:
                return {
                    'status': 'ok', 
                    'message': f'Dados atualizados há {diff_hours:.1f} horas',
                    'last_update': ultima_atualizacao.isoformat()
                }
            else:
                return {
                    'status': 'warning', 
                    'message': f'Dados desatualizados há {diff_hours:.1f} horas',
                    'last_update': ultima_atualizacao.isoformat()
                }
                
        except Exception as e:
            return {'status': 'error', 'message': f'Erro ao verificar atualização: {str(e)}'}
    
    def _check_data_quality(self) -> Dict[str, Any]:
        """Verifica qualidade básica dos dados."""
        
        try:
            hook = BigQueryHook(gcp_conn_id='google_cloud_default')
            
            # Verificações básicas
            checks = []
            
            # 1. Verificar se há dados nas tabelas
            query = """
            SELECT 
                table_name,
                row_count
            FROM `dataglowup-458411.DataGlowUp_mart.__TABLES__`
            WHERE table_name LIKE 'mart_%'
            """
            
            result = hook.get_pandas_df(query)
            
            for _, row in result.iterrows():
                if row['row_count'] == 0:
                    checks.append(f"Tabela {row['table_name']} está vazia")
            
            if checks:
                return {'status': 'warning', 'message': f'Problemas encontrados: {"; ".join(checks)}'}
            else:
                return {'status': 'ok', 'message': 'Qualidade dos dados OK'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Erro ao verificar qualidade: {str(e)}'}
