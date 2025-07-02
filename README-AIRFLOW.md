# 🚀 DGU Futebol - Apache Airflow 3.0

Documentação completa para execução do pipeline DGU com Apache Airflow 3.0.

## 📋 Visão Geral

O Apache Airflow orquestra automaticamente o pipeline de dados de futebol, executando:

- **Extração de dados** dos sites fbref.com e transfermarkt.com
- **Processamento via dbt** (staging e mart)
- **Carregamento no BigQuery**
- **Monitoramento e alertas**

### 🕐 Agendamento Automático

- **Terças-feiras às 09:00** - Execução completa do pipeline
- **Sextas-feiras às 09:00** - Execução completa do pipeline
- **Diariamente às 10:00** - Monitoramento e verificações de qualidade

## 🚀 Início Rápido

### 1. Configuração Inicial (5 min)

```bash
# Preparar credenciais
mkdir -p credentials
cp /caminho/para/suas/credenciais.json credentials/bigquery-credentials.json

# Configurar dbt
cp DGU/profiles.yml.example DGU/profiles.yml
# Editar DGU/profiles.yml com suas configurações

# Inicializar Airflow
./docker-scripts.sh init-airflow
```

### 2. Acessar Interface Web

```bash
# Abrir no navegador
http://localhost:8080

# Credenciais padrão
Usuário: airflow
Senha: airflow
```

### 3. Ativar DAGs

Na interface web do Airflow:
1. Acesse a página principal
2. Ative as DAGs:
   - `dgu_futebol_pipeline` (Pipeline principal)
   - `dgu_monitoring` (Monitoramento)

## 📊 DAGs Disponíveis

### 🏆 `dgu_futebol_pipeline`
**Pipeline principal de dados de futebol**

- **Agendamento**: Terças e sextas às 09:00
- **Duração**: ~30-45 minutos
- **Tasks**:
  1. Extração de estatísticas (fbref.com)
  2. Extração de valores de mercado (transfermarkt.com)
  3. Processamento e salvamento de seeds
  4. Verificação de dados extraídos
  5. dbt seed (carregamento no BigQuery)
  6. dbt run staging (views de limpeza)
  7. dbt run mart (tabelas finais)
  8. dbt test (validações)
  9. Verificação BigQuery
  10. Notificação de sucesso

### 📈 `dgu_monitoring`
**Monitoramento e qualidade de dados**

- **Agendamento**: Diariamente às 10:00
- **Duração**: ~5-10 minutos
- **Tasks**:
  1. Verificação de existência de tabelas
  2. Verificação de dados nas tabelas
  3. Verificação de atualização dos dados
  4. Verificação de qualidade dos dados
  5. Geração de relatório diário

## 🛠️ Comandos Úteis

### Gerenciamento do Airflow

```bash
# Inicializar Airflow
./docker-scripts.sh init-airflow

# Executar via Airflow
./docker-scripts.sh run-airflow

# Ver logs do Airflow
./docker-scripts.sh logs-airflow

# Parar Airflow
./docker-scripts.sh stop-airflow

# Ver status dos containers
./docker-scripts.sh status
```

### Comandos Docker Compose

```bash
# Iniciar todos os serviços
docker-compose -f docker-compose-integrated.yml up -d

# Ver logs específicos
docker-compose -f docker-compose-integrated.yml logs -f airflow-scheduler

# Reiniciar serviço específico
docker-compose -f docker-compose-integrated.yml restart airflow-webserver

# Parar todos os serviços
docker-compose -f docker-compose-integrated.yml down
```

### Comandos CLI do Airflow

```bash
# Acessar CLI do Airflow
docker-compose -f docker-compose-integrated.yml exec airflow-webserver bash

# Listar DAGs
airflow dags list

# Executar DAG manualmente
airflow dags trigger dgu_futebol_pipeline

# Ver status de execução
airflow dags state dgu_futebol_pipeline 2024-01-01

# Listar tasks de uma DAG
airflow tasks list dgu_futebol_pipeline
```

## 📁 Estrutura de Arquivos

```
projeto/
├── airflow/
│   ├── dags/
│   │   ├── dgu_futebol_pipeline.py    # DAG principal
│   │   └── dgu_monitoring.py          # DAG de monitoramento
│   ├── plugins/
│   │   ├── dgu_operators.py           # Operadores customizados
│   │   └── dgu_alerts.py              # Sistema de alertas
│   ├── config/
│   │   └── airflow.cfg                # Configuração do Airflow
│   ├── logs/                          # Logs do Airflow
│   ├── setup_airflow_connections.py   # Script de configuração
│   └── init_airflow.sh               # Script de inicialização
├── docker-compose-airflow.yml         # Compose apenas Airflow
├── docker-compose-integrated.yml      # Compose integrado
└── Dockerfile.airflow                 # Imagem customizada
```

## ⚙️ Configurações Avançadas

### Variáveis do Airflow

As seguintes variáveis são configuradas automaticamente:

```python
# Configurações do projeto
dgu_project_id = 'dataglowup-458411'
dgu_dataset_main = 'DataGlowUp'
dgu_dataset_staging = 'DataGlowUp_staging'
dgu_dataset_mart = 'DataGlowUp_mart'

# Configurações de execução
dgu_max_retries = '3'
dgu_timeout_minutes = '120'
dgu_email_alerts = 'admin@dgu.com'

# Configurações de monitoramento
dgu_data_freshness_hours = '96'  # 4 dias
dgu_min_players_per_team = '15'
dgu_max_players_per_team = '50'
```

### Conexões

- **`google_cloud_default`**: Conexão com BigQuery
- Configurada automaticamente com as credenciais fornecidas

### Pools de Recursos

- **`dgu_extraction_pool`**: 2 slots para extração
- **`dgu_bigquery_pool`**: 3 slots para BigQuery
- **`dgu_dbt_pool`**: 1 slot para dbt

## 🔔 Sistema de Alertas

### Canais Suportados

1. **Log** (padrão): Alertas nos logs do Airflow
2. **Slack**: Configure `dgu_slack_webhook`
3. **Teams**: Configure `dgu_teams_webhook`
4. **Email**: Configure `dgu_email_alerts`

### Configurar Slack

```bash
# Via interface web do Airflow
Admin > Variables > Create
Key: dgu_slack_webhook
Value: https://hooks.slack.com/services/...
```

### Configurar Teams

```bash
# Via interface web do Airflow
Admin > Variables > Create
Key: dgu_teams_webhook
Value: https://outlook.office.com/webhook/...
```

## 📊 Monitoramento

### Interface Web

- **URL**: http://localhost:8080
- **DAGs**: Visualizar status e histórico
- **Logs**: Logs detalhados de cada task
- **Gantt**: Timeline de execução
- **Graph**: Dependências entre tasks

### Métricas Importantes

- **Taxa de sucesso**: % de execuções bem-sucedidas
- **Duração média**: Tempo médio de execução
- **Última execução**: Timestamp da última execução
- **Próxima execução**: Próximo agendamento

## 🐛 Solução de Problemas

### Airflow não inicia

```bash
# Verificar logs
docker-compose -f docker-compose-integrated.yml logs airflow-init

# Verificar permissões
export AIRFLOW_UID=$(id -u)
sudo chown -R $AIRFLOW_UID:0 airflow/

# Reconstruir imagem
docker-compose -f docker-compose-integrated.yml build --no-cache
```

### DAG não aparece

```bash
# Verificar sintaxe Python
python airflow/dags/dgu_futebol_pipeline.py

# Verificar logs do scheduler
docker-compose -f docker-compose-integrated.yml logs airflow-scheduler

# Forçar refresh
docker-compose -f docker-compose-integrated.yml exec airflow-webserver airflow dags reserialize
```

### Erro de conexão BigQuery

```bash
# Verificar credenciais
ls -la credentials/bigquery-credentials.json

# Testar conexão
docker-compose -f docker-compose-integrated.yml exec airflow-webserver python -c "
from google.cloud import bigquery
client = bigquery.Client()
print('Conexão OK!')
"

# Reconfigurar conexão
docker-compose -f docker-compose-integrated.yml exec airflow-webserver python /opt/airflow/project/airflow/setup_airflow_connections.py
```

### Task falha constantemente

```bash
# Ver logs detalhados da task
# Na interface web: DAGs > dgu_futebol_pipeline > Graph > [Task] > Logs

# Executar task manualmente
docker-compose -f docker-compose-integrated.yml exec airflow-webserver airflow tasks test dgu_futebol_pipeline extrair_estatisticas 2024-01-01

# Verificar recursos
docker stats
```

## 🔄 Backup e Recuperação

### Backup do Banco de Dados

```bash
# Backup do PostgreSQL
docker-compose -f docker-compose-integrated.yml exec postgres pg_dump -U airflow airflow > backup_airflow.sql

# Restaurar backup
docker-compose -f docker-compose-integrated.yml exec -T postgres psql -U airflow airflow < backup_airflow.sql
```

### Backup de Configurações

```bash
# Backup de variáveis e conexões
docker-compose -f docker-compose-integrated.yml exec airflow-webserver airflow variables export variables_backup.json
docker-compose -f docker-compose-integrated.yml exec airflow-webserver airflow connections export connections_backup.json
```

## 📈 Próximos Passos

1. **Configurar alertas** via Slack/Teams
2. **Implementar testes** adicionais de qualidade
3. **Adicionar mais times** ao pipeline
4. **Configurar backup** automático
5. **Implementar CI/CD** para atualizações

## 🎯 Resumo dos Benefícios

### ✅ Automação Completa
- Execução automática nas terças e sextas às 09:00
- Monitoramento diário às 10:00
- Retry automático em caso de falhas

### ✅ Visibilidade Total
- Interface web intuitiva
- Logs detalhados de cada etapa
- Métricas de performance

### ✅ Confiabilidade
- Verificações de qualidade automáticas
- Alertas em tempo real
- Backup e recuperação

### ✅ Escalabilidade
- Fácil adição de novos times
- Configuração flexível
- Recursos otimizados

---

**🎯 Pipeline de dados de futebol totalmente automatizado com Apache Airflow 3.0!**

Para documentação completa do Docker, veja: [README-Docker.md](README-Docker.md)
