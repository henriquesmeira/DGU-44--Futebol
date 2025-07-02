# ⚡ Início Rápido - Apache Airflow 3.0

Guia de 10 minutos para executar o pipeline DGU com orquestração automática via Airflow.

## 🚀 Setup em 4 Passos

### 1. Preparar Credenciais (2 min)

```bash
# Criar pasta para credenciais
mkdir -p credentials

# Copiar suas credenciais do BigQuery
cp /caminho/para/suas/credenciais.json credentials/bigquery-credentials.json
```

### 2. Configurar dbt (1 min)

```bash
# Copiar template
cp DGU/profiles.yml.example DGU/profiles.yml

# Editar com seus dados (substitua os valores)
sed -i 's/seu-project-id/SEU_PROJECT_ID_REAL/g' DGU/profiles.yml
sed -i 's|/caminho/para/seu/arquivo-credenciais.json|/opt/airflow/credentials/bigquery-credentials.json|g' DGU/profiles.yml
```

### 3. Inicializar Airflow (5 min)

```bash
# Executar script de inicialização
./docker-scripts.sh init-airflow

# Aguardar inicialização (será exibido progresso)
```

### 4. Acessar Interface Web (2 min)

```bash
# Abrir no navegador
http://localhost:8080

# Fazer login
Usuário: airflow
Senha: airflow

# Ativar DAGs
1. Clique no toggle das DAGs:
   - dgu_futebol_pipeline ✅
   - dgu_monitoring ✅
```

## 🎯 Execução Automática

### 📅 Agendamento Configurado

- **Pipeline Principal**: Terças e sextas às 09:00
- **Monitoramento**: Diariamente às 10:00

### ▶️ Execução Manual (Teste)

```bash
# Na interface web do Airflow:
1. Acesse "DAGs"
2. Clique em "dgu_futebol_pipeline"
3. Clique no botão "Trigger DAG" (▶️)
4. Acompanhe o progresso na aba "Graph"
```

## 📊 Monitoramento

### Interface Web - Principais Seções

- **DAGs**: Lista e status das DAGs
- **Graph**: Visualização das dependências
- **Gantt**: Timeline de execução
- **Logs**: Logs detalhados de cada task

### 📈 Métricas Importantes

```bash
# Verificar última execução
DAGs > dgu_futebol_pipeline > Last Run

# Ver logs de uma task específica
Graph > [Nome da Task] > Logs

# Histórico de execuções
Browse > Task Instances
```

## 🔧 Comandos Úteis

### Gerenciamento Rápido

```bash
# Ver status dos serviços
./docker-scripts.sh status

# Ver logs em tempo real
./docker-scripts.sh logs-airflow

# Parar Airflow
./docker-scripts.sh stop-airflow

# Reiniciar Airflow
./docker-scripts.sh stop-airflow
./docker-scripts.sh run-airflow
```

### Comandos Avançados

```bash
# Executar DAG via CLI
docker-compose -f docker-compose-integrated.yml exec airflow-webserver \
  airflow dags trigger dgu_futebol_pipeline

# Listar todas as DAGs
docker-compose -f docker-compose-integrated.yml exec airflow-webserver \
  airflow dags list

# Ver status de uma execução
docker-compose -f docker-compose-integrated.yml exec airflow-webserver \
  airflow dags state dgu_futebol_pipeline 2024-01-01
```

## ✅ Verificar Resultados

### 1. No Airflow (Interface Web)

```bash
# Verificar se pipeline executou com sucesso
DAGs > dgu_futebol_pipeline > Graph
# Todas as tasks devem estar verdes ✅
```

### 2. No BigQuery Console

```bash
# Acessar: https://console.cloud.google.com/bigquery

# Verificar datasets criados:
1. DataGlowUp (dados brutos) - 6 tabelas
2. DataGlowUp_staging (views) - 6 views  
3. DataGlowUp_mart (finais) - 3 tabelas
```

### 3. Logs do Sistema

```bash
# Ver logs da última execução
./docker-scripts.sh logs-airflow | grep "dgu_futebol_pipeline"

# Verificar se não há erros
./docker-scripts.sh logs-airflow | grep -i error
```

## 🐛 Solução Rápida de Problemas

### Airflow não carrega

```bash
# Verificar se Docker está rodando
docker ps

# Verificar logs de inicialização
docker-compose -f docker-compose-integrated.yml logs airflow-init

# Reconstruir se necessário
docker-compose -f docker-compose-integrated.yml build --no-cache
```

### DAG não aparece

```bash
# Verificar sintaxe do arquivo Python
python airflow/dags/dgu_futebol_pipeline.py

# Forçar refresh das DAGs
# Na interface web: Admin > Configuration > Refresh
```

### Erro de credenciais

```bash
# Verificar se arquivo existe
ls -la credentials/bigquery-credentials.json

# Verificar permissões
chmod 600 credentials/bigquery-credentials.json

# Testar conexão
docker-compose -f docker-compose-integrated.yml exec airflow-webserver python -c "
from google.cloud import bigquery
client = bigquery.Client()
print('✅ Conexão OK!')
"
```

### Pipeline falha

```bash
# Ver logs específicos da task que falhou
# Interface web: Graph > [Task Vermelha] > Logs

# Executar task manualmente para debug
docker-compose -f docker-compose-integrated.yml exec airflow-webserver \
  airflow tasks test dgu_futebol_pipeline extrair_estatisticas 2024-01-01
```

## 🎉 Próximos Passos

### 1. Configurar Alertas

```bash
# Slack (opcional)
Admin > Variables > Create
Key: dgu_slack_webhook
Value: https://hooks.slack.com/services/...

# Email (opcional)
Admin > Variables > Create
Key: dgu_email_alerts
Value: seu-email@exemplo.com
```

### 2. Personalizar Agendamento

```bash
# Editar arquivo da DAG
nano airflow/dags/dgu_futebol_pipeline.py

# Alterar linha:
schedule_interval='0 9 * * 2,5'  # Terças e sextas às 09:00

# Para executar diariamente às 08:00:
schedule_interval='0 8 * * *'
```

### 3. Adicionar Mais Times

```bash
# Editar extract.py para incluir novos times
# Atualizar dbt_project.yml com configurações dos novos seeds
# Recriar modelos dbt conforme necessário
```

## 📚 Documentação Completa

- **Airflow**: [README-AIRFLOW.md](README-AIRFLOW.md)
- **Docker**: [README-Docker.md](README-Docker.md)
- **Projeto**: [PROJETO_COMPLETO.md](PROJETO_COMPLETO.md)

---

**⚡ Em 10 minutos você tem um pipeline de dados de futebol totalmente automatizado!**

**🕐 Execução automática**: Terças e sextas às 09:00  
**📊 Monitoramento**: http://localhost:8080  
**🎯 Dados atualizados**: BigQuery Console
