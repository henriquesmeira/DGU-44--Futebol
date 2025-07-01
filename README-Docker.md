# 🐳 DGU Futebol - Execução com Docker

Este guia explica como executar o pipeline de dados de futebol usando Docker.

## 📋 Pré-requisitos

1. **Docker** e **Docker Compose** instalados
2. **Credenciais do BigQuery** (arquivo JSON)
3. **Arquivo profiles.yml** configurado

## 🚀 Configuração Rápida

### 1. Preparar Credenciais

```bash
# Criar diretório para credenciais
mkdir -p credentials

# Copiar seu arquivo de credenciais do BigQuery
cp /caminho/para/suas/credenciais.json credentials/bigquery-credentials.json
```

### 2. Configurar profiles.yml

```bash
# Copiar o exemplo
cp DGU/profiles.yml.example DGU/profiles.yml

# Editar com suas configurações
nano DGU/profiles.yml
```

Exemplo de configuração:
```yaml
DGU:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: /app/credentials/bigquery-credentials.json
      project: seu-project-id
      dataset: DataGlowUp
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive
      retries: 1
```

### 3. Executar o Pipeline

```bash
# Construir e executar
docker-compose up --build

# Ou executar em background
docker-compose up -d --build
```

## 📊 Comandos Úteis

### Pipeline Completo
```bash
# Executar pipeline completo (extração + dbt)
docker-compose run --rm dgu-futebol python main.py
```

### Comandos dbt Manuais
```bash
# Executar apenas seeds
docker-compose run --rm dgu-futebol bash -c "cd DGU && dbt seed --profiles-dir ."

# Executar apenas staging
docker-compose run --rm dgu-futebol bash -c "cd DGU && dbt run --select staging --profiles-dir ."

# Executar apenas mart
docker-compose run --rm dgu-futebol bash -c "cd DGU && dbt run --select mart --profiles-dir ."

# Executar testes
docker-compose run --rm dgu-futebol bash -c "cd DGU && dbt test --profiles-dir ."
```

### Comandos de Debug
```bash
# Acessar shell do container
docker-compose run --rm dgu-futebol bash

# Ver logs em tempo real
docker-compose logs -f dgu-futebol

# Verificar status dos containers
docker-compose ps
```

## 📁 Estrutura de Volumes

```
projeto/
├── credentials/
│   └── bigquery-credentials.json  # Suas credenciais (não commitadas)
├── logs/                          # Logs persistidos
├── DGU/
│   ├── seeds/                     # CSVs gerados
│   └── profiles.yml               # Configuração dbt
└── docker-compose.yml
```

## 🔧 Personalização

### Variáveis de Ambiente

Você pode personalizar o comportamento através de variáveis de ambiente:

```bash
# Arquivo .env (opcional)
PROJECT_ID=seu-project-id
DATASET_ID=SeuDataset
```

### Recursos do Container

Edite `docker-compose.yml` para ajustar recursos:

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Aumentar se necessário
      cpus: '2.0'
```

## 🐛 Solução de Problemas

### Erro de Credenciais
```bash
# Verificar se o arquivo existe
ls -la credentials/

# Verificar permissões
chmod 600 credentials/bigquery-credentials.json
```

### Erro de Conexão BigQuery
```bash
# Testar conexão manualmente
docker-compose run --rm dgu-futebol python -c "
from google.cloud import bigquery
client = bigquery.Client()
print('Conexão OK!')
"
```

### Limpar Ambiente
```bash
# Parar containers
docker-compose down

# Remover volumes (cuidado!)
docker-compose down -v

# Limpar imagens
docker system prune -a
```

## 📈 Monitoramento

### Ver Progresso
```bash
# Logs em tempo real
docker-compose logs -f

# Status dos containers
docker-compose ps

# Uso de recursos
docker stats
```

### Verificar Resultados
Após a execução, verifique no BigQuery Console:
- Dataset `DataGlowUp` (dados brutos)
- Dataset `DataGlowUp_staging` (views)
- Dataset `DataGlowUp_mart` (tabelas finais)

## 🔄 Execução Agendada

Para execução automática, você pode usar cron:

```bash
# Adicionar ao crontab
0 6 * * * cd /caminho/do/projeto && docker-compose run --rm dgu-futebol python main.py
```

## 📚 Próximos Passos

1. Configure alertas de monitoramento
2. Implemente backup dos dados
3. Configure CI/CD para atualizações automáticas
4. Adicione mais fontes de dados

---

**🏆 Pipeline de dados de futebol containerizado e pronto para produção!**
