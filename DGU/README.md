# Projeto DGU - Data Pipeline de Futebol com dbt

Este projeto implementa um pipeline de dados completo para análise de estatísticas de futebol dos principais times brasileiros (Palmeiras, Flamengo e Corinthians) usando dbt e BigQuery.

## 🏗️ Arquitetura do Pipeline

### Camadas de Dados:

1. **Seeds** → Dados brutos importados
2. **Staging** → Limpeza e padronização (Views)
3. **Mart** → Tabelas finais para análise (Tables)

### 📊 Fontes de Dados:

- **fbref.com**: Estatísticas detalhadas dos jogadores
- **transfermarkt.com**: Valores de mercado e informações contratuais

## 🚀 Como Executar

### Opção 1: Script Automatizado
```bash
./load_seeds.sh
```

### Opção 2: Comandos Manuais
```bash
cd DGU
source ../dbt-env/bin/activate  # se necessário
dbt seed                        # Carrega dados brutos
dbt run                         # Executa transformações
dbt test                        # Executa testes de qualidade
```

## 📁 Estrutura do Projeto

```
DGU/
├── seeds/                      # Dados brutos (CSV)
│   ├── *_tabela_0.csv         # Estatísticas dos jogadores
│   └── *_tabela_0_mercado.csv # Valores de mercado
├── models/
│   ├── staging/               # Camada de limpeza (Views)
│   │   ├── stg_*_stats.sql   # Estatísticas padronizadas
│   │   └── stg_*_market.sql  # Valores de mercado padronizados
│   └── mart/                  # Camada analítica (Tables)
│       ├── mart_players_stats.sql        # Todos os jogadores
│       ├── mart_players_market_value.sql # Valores consolidados
│       └── mart_teams_summary.sql        # Resumo por time
└── profiles.yml               # Configuração BigQuery
```

## 📈 Datasets Criados no BigQuery

### `DataGlowUp` (Principal)
- Seeds com dados brutos dos times

### `DataGlowUp_staging`
- Views com dados limpos e padronizados
- Transformações básicas e cálculos derivados

### `DataGlowUp_mart`
- **mart_players_stats**: Estatísticas consolidadas de todos os jogadores
- **mart_players_market_value**: Valores de mercado e análises contratuais
- **mart_teams_summary**: Resumo executivo por time

## 🔍 Principais Métricas Disponíveis

### Estatísticas dos Jogadores:
- Gols, assistências, cartões
- Métricas por 90 minutos
- Expected Goals (xG) e Expected Assists (xA)
- Classificação de performance

### Análise de Mercado:
- Valores em euros e classificações
- Status contratuais
- Perfis de valor por idade
- Análises de potencial

### Resumo por Time:
- Estatísticas agregadas
- Valor total do elenco
- Composição por posição
- Classificações comparativas

## 🎯 Casos de Uso

1. **Análise de Performance**: Compare jogadores entre times
2. **Scouting**: Identifique talentos e oportunidades
3. **Gestão Financeira**: Analise valores de elenco
4. **Planejamento**: Monitore contratos e renovações

## 📋 Comandos Úteis

```bash
# Executar apenas staging
dbt run --select staging

# Executar apenas mart
dbt run --select mart

# Recarregar seeds
dbt seed --full-refresh

# Executar testes
dbt test

# Gerar documentação
dbt docs generate
dbt docs serve
```

## 🔧 Configuração

Certifique-se de que:
1. O arquivo de credenciais JSON está no diretório raiz
2. O `profiles.yml` aponta para o projeto correto no BigQuery
3. O ambiente virtual dbt está ativado

## 📚 Recursos Adicionais

- [Documentação dbt](https://docs.getdbt.com/)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/)
- [Guia de Seeds dbt](https://docs.getdbt.com/docs/building-a-dbt-project/seeds)
