# Seeds do Projeto DGU - Dados de Futebol

Este diretório contém os arquivos seeds do dbt com dados de exemplo dos times de futebol brasileiros.

## Estrutura dos Dados

### Tabelas de Estatísticas dos Jogadores
- `palmeiras_tabela_0.csv` - Estatísticas dos jogadores do Palmeiras
- `flamengo_tabela_0.csv` - Estatísticas dos jogadores do Flamengo  
- `corinthians_tabela_0.csv` - Estatísticas dos jogadores do Corinthians

**Colunas das tabelas de estatísticas:**
- `player`: Nome do jogador
- `nation`: Nacionalidade (código do país)
- `pos`: Posição (GK, DF, MC, AT)
- `age`: Idade
- `mp`: Jogos disputados
- `starts`: Jogos como titular
- `min`: Minutos jogados
- `90s`: Jogos de 90 minutos equivalentes
- `gls`: Gols marcados
- `ast`: Assistências
- `g_a`: Gols + Assistências
- `g_pk`: Gols sem pênaltis
- `pk`: Pênaltis convertidos
- `pkatt`: Pênaltis tentados
- `crdy`: Cartões amarelos
- `crdr`: Cartões vermelhos
- `xg`: Expected Goals
- `npxg`: Expected Goals sem pênaltis
- `xag`: Expected Assists
- `npxg_xag`: Expected Goals + Expected Assists sem pênaltis
- `prgc`: Carries progressivos
- `prgp`: Passes progressivos
- `prgr`: Recepções progressivas
- `time`: Nome do time
- `data_extracao`: Data e hora da extração
- `fonte`: URL da fonte dos dados

### Tabelas de Valor de Mercado
- `palmeiras_tabela_0_mercado.csv` - Valores de mercado dos jogadores do Palmeiras
- `flamengo_tabela_0_mercado.csv` - Valores de mercado dos jogadores do Flamengo
- `corinthians_tabela_0_mercado.csv` - Valores de mercado dos jogadores do Corinthians

**Colunas das tabelas de valor de mercado:**
- `player`: Nome do jogador
- `position`: Posição detalhada
- `age`: Idade
- `nationality`: Nacionalidade
- `market_value_eur`: Valor de mercado em euros
- `contract_expires`: Data de expiração do contrato
- `time`: Nome do time
- `data_extracao`: Data e hora da extração
- `fonte`: URL da fonte dos dados

## Como usar

1. **Carregar os seeds no BigQuery:**
   ```bash
   cd DGU
   dbt seed
   ```

2. **Carregar apenas um seed específico:**
   ```bash
   dbt seed --select palmeiras_tabela_0
   ```

3. **Recarregar todos os seeds (sobrescrever dados existentes):**
   ```bash
   dbt seed --full-refresh
   ```

## Configurações

As configurações dos seeds estão definidas no arquivo `dbt_project.yml` na seção `seeds`, incluindo:
- Tipos de dados específicos para cada coluna
- Configurações de materialização

## Fontes dos Dados

- **Estatísticas**: fbref.com - Dados de performance dos jogadores
- **Valor de Mercado**: transfermarkt.com - Valores de mercado e informações contratuais

## Observações

- Os dados são de exemplo e representam a estrutura esperada dos dados reais
- As datas de extração são fixas para fins de demonstração
- Os valores de mercado estão em euros
- As estatísticas seguem o padrão do fbref.com
