{{ config(materialized='table') }}

with all_teams_stats as (
    -- União de todas as estatísticas dos times
    select * from {{ ref('stg_palmeiras_stats') }}
    union all
    select * from {{ ref('stg_flamengo_stats') }}
    union all
    select * from {{ ref('stg_corinthians_stats') }}
),

final_stats as (
    select
        -- Identificadores únicos
        concat(team_name, '_', player_name) as player_id,
        player_name,
        team_name,
        nationality_code,
        position_code,
        position_full_name,
        age,
        
        -- Estatísticas de participação
        matches_played,
        matches_started,
        minutes_played,
        matches_90min_equivalent,
        
        -- Estatísticas ofensivas
        goals,
        assists,
        goals_assists,
        goals_non_penalty,
        penalties_made,
        penalties_attempted,
        
        -- Métricas por 90 minutos
        goals_per_90min,
        assists_per_90min,
        
        -- Métricas avançadas
        expected_goals,
        expected_goals_non_penalty,
        expected_assists,
        expected_goals_assists_non_penalty,
        
        -- Progressão
        progressive_carries,
        progressive_passes,
        progressive_receptions,
        
        -- Disciplina
        yellow_cards,
        red_cards,
        
        -- Eficiência de pênaltis
        case 
            when penalties_attempted > 0 then round(cast(penalties_made as float64) / cast(penalties_attempted as float64) * 100, 1)
            else null 
        end as penalty_conversion_rate,
        
        -- Classificação de performance
        case 
            when goals_per_90min >= 0.8 then 'Excellent Scorer'
            when goals_per_90min >= 0.5 then 'Good Scorer'
            when goals_per_90min >= 0.3 then 'Average Scorer'
            when goals_per_90min > 0 then 'Occasional Scorer'
            else 'Non-Scorer'
        end as scoring_classification,
        
        -- Metadados
        extraction_date,
        source_url,
        current_timestamp() as processed_at
        
    from all_teams_stats
    where player_name is not null
)

select * from final_stats
order by team_name, goals desc, assists desc
