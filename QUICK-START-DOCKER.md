# 🚀 Início Rápido - Docker

Guia de 5 minutos para executar o pipeline DGU com Docker.

## ⚡ Setup Rápido

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
sed -i 's|/caminho/para/seu/arquivo-credenciais.json|/app/credentials/bigquery-credentials.json|g' DGU/profiles.yml
```

### 3. Executar Pipeline (2 min)

```bash
# Opção A: Script automatizado (recomendado)
./docker-scripts.sh setup
./docker-scripts.sh run

# Opção B: Docker Compose direto
docker-compose up --build
```

## 🎯 Comandos Essenciais

```bash
# Ver progresso em tempo real
./docker-scripts.sh logs

# Executar apenas extração de dados
docker-compose run --rm dgu-futebol python extract.py

# Executar apenas dbt
./docker-scripts.sh dbt "run"

# Acessar shell para debug
./docker-scripts.sh shell

# Ver status
./docker-scripts.sh status

# Limpar tudo
./docker-scripts.sh clean
```

## ✅ Verificar Resultados

Após execução bem-sucedida, verifique no BigQuery:

1. **Dataset `DataGlowUp`** - 6 tabelas com dados brutos
2. **Dataset `DataGlowUp_staging`** - 6 views limpas  
3. **Dataset `DataGlowUp_mart`** - 3 tabelas finais

## 🐛 Problemas Comuns

### Erro de Credenciais
```bash
# Verificar se arquivo existe
ls -la credentials/bigquery-credentials.json

# Verificar conteúdo do profiles.yml
cat DGU/profiles.yml
```

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs dgu-futebol

# Reconstruir imagem
docker-compose build --no-cache
```

### Erro de permissão
```bash
# Corrigir permissões
chmod 600 credentials/bigquery-credentials.json
chmod +x docker-scripts.sh
```

## 📊 Próximos Passos

1. **Agendar execução**: Configure cron para execução automática
2. **Monitorar**: Configure alertas no BigQuery
3. **Expandir**: Adicione mais times ou métricas
4. **Otimizar**: Ajuste recursos do container conforme necessário

---

**🏆 Em 5 minutos você tem um pipeline de dados de futebol rodando em produção!**

Para documentação completa, veja: [README-Docker.md](README-Docker.md)
