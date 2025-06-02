# 🏆 Projeto DGU - Pipeline de Dados de Futebol

Pipeline completo de extração, transformação e análise de dados de futebol dos principais times brasileiros usando Python, dbt e BigQuery.

## ⚙️ Configuração Inicial

1. **Configure o profiles.yml:**
   ```bash
   cp DGU/profiles.yml.example DGU/profiles.yml
   # Edite DGU/profiles.yml com suas credenciais
   ```

2. **Adicione suas credenciais BigQuery** no diretório raiz

## 🚀 Execução Simples

```bash
# Ativar ambiente virtual
source dbt-env/bin/activate

# Executar pipeline completo
python main.py
```

## 📊 O que o Pipeline Faz

1. **📈 Extrai dados reais** do fbref.com e transfermarkt.com
2. **💾 Salva como seeds** CSV para o dbt
3. **🌱 Carrega no BigQuery** (dataset DataGlowUp)
4. **🔄 Cria views staging** (dataset DataGlowUp_staging)
5. **📊 Cria tabelas mart** (dataset DataGlowUp_mart)

## 🎯 Dados Coletados

### Times Analisados:
- **Palmeiras** ⚽
- **Flamengo** ⚽  
- **Corinthians** ⚽

### Métricas Extraídas:
- **Estatísticas dos jogadores**: Gols, assistências, cartões, xG, xA
- **Valores de mercado**: Preços em euros, contratos, posições
- **Análises agregadas**: Resumos por time, classificações

## 📁 Estrutura do Projeto

```
├── main.py                    # 🚀 Script principal
├── extract.py                 # 📊 Extração de dados
├── load.py                    # 📤 Carregamento BigQuery
├── dataglowup-*.json         # 🔑 Credenciais
├── dbt-env/                   # 🐍 Ambiente Python
└── DGU/                       # 📦 Projeto dbt
    ├── seeds/                 # 📄 Dados CSV
    ├── models/staging/        # 🔄 Views limpas
    └── models/mart/           # 📊 Tabelas finais
```

## 📈 Resultados no BigQuery

### Dataset `DataGlowUp` (Seeds)
- 6 tabelas com dados brutos extraídos

### Dataset `DataGlowUp_staging` (Views)  
- 6 views com dados limpos e padronizados

### Dataset `DataGlowUp_mart` (Tabelas)
- `mart_players_stats` - Estatísticas consolidadas
- `mart_players_market_value` - Análise de valores
- `mart_teams_summary` - Resumo por time

## 🛠️ Tecnologias

- **Python** - Extração e orquestração
- **dbt** - Transformação de dados
- **BigQuery** - Data warehouse
- **Pandas** - Manipulação de dados
- **BeautifulSoup** - Web scraping

## 📚 Documentação Completa

Veja `PROJETO_COMPLETO.md` para documentação detalhada.

---

**Desenvolvido para análise de dados de futebol brasileiro** ⚽🇧🇷
