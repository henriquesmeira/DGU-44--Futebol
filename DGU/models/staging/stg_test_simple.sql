{{ config(materialized='view') }}

-- Teste simples para verificar se o staging funciona
select
    player as player_name,
    `time` as team_name,
    age,
    gls as goals
from {{ ref('palmeiras_tabela_0') }}
limit 5
