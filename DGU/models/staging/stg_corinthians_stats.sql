{{ config(materialized='view') }}

with source_data as (
    select * from {{ ref('corinthians_tabela_0') }}
),

cleaned_data as (
    select
        -- Identificadores
        player as player_name,
        nation as nationality_code,
        pos as position_code,
        time as team_name,
        
        -- Informações básicas
        age,
        mp as matches_played,
        starts as matches_started,
        min as minutes_played,
        `90s` as matches_90min_equivalent,
        
        -- Estatísticas ofensivas
        gls as goals,
        ast as assists,
        `g_a` as goals_assists,
        `g_pk` as goals_non_penalty,
        pk as penalties_made,
        pkatt as penalties_attempted,
        
        -- Disciplina
        crdy as yellow_cards,
        crdr as red_cards,
        
        -- Métricas avançadas
        xg as expected_goals,
        npxg as expected_goals_non_penalty,
        xag as expected_assists,
        `npxg_xag` as expected_goals_assists_non_penalty,
        
        -- Progressão
        prgc as progressive_carries,
        prgp as progressive_passes,
        prgr as progressive_receptions,
        
        -- Metadados
        `data_extracao` as extraction_date,
        fonte as source_url,
        
        -- Campos calculados
        case 
            when min > 0 then round(cast(gls as float64) / (cast(min as float64) / 90), 2)
            else 0 
        end as goals_per_90min,
        
        case 
            when min > 0 then round(cast(ast as float64) / (cast(min as float64) / 90), 2)
            else 0 
        end as assists_per_90min,
        
        case 
            when pos = 'GK' then 'Goalkeeper'
            when pos = 'DF' then 'Defender'
            when pos = 'MC' then 'Midfielder'
            when pos = 'AT' then 'Attacker'
            else 'Unknown'
        end as position_full_name
        
    from source_data
)

select * from cleaned_data
