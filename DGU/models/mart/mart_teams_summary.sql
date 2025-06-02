{{ config(materialized='table') }}

with team_stats as (
    select
        team_name,
        count(*) as total_players,
        sum(goals) as total_goals,
        sum(assists) as total_assists,
        sum(goals_assists) as total_goal_contributions,
        avg(age) as avg_age,
        sum(minutes_played) as total_minutes,
        sum(yellow_cards) as total_yellow_cards,
        sum(red_cards) as total_red_cards,
        avg(expected_goals) as avg_expected_goals,
        avg(expected_assists) as avg_expected_assists
    from {{ ref('mart_players_stats') }}
    group by team_name
),

team_market as (
    select
        team_name,
        sum(market_value_euros) as total_squad_value_euros,
        avg(market_value_euros) as avg_player_value_euros,
        max(market_value_euros) as highest_valued_player_euros,
        min(market_value_euros) as lowest_valued_player_euros,
        sum(case when contract_status = 'Expiring Soon' then 1 else 0 end) as players_expiring_soon,
        sum(case when market_value_category = 'Very High' then 1 else 0 end) as very_high_value_players
    from {{ ref('mart_players_market_value') }}
    group by team_name
),

team_positions as (
    select
        team_name,
        sum(case when position_full_name = 'Goalkeeper' then 1 else 0 end) as goalkeepers,
        sum(case when position_full_name = 'Defender' then 1 else 0 end) as defenders,
        sum(case when position_full_name = 'Midfielder' then 1 else 0 end) as midfielders,
        sum(case when position_full_name = 'Attacker' then 1 else 0 end) as attackers
    from {{ ref('mart_players_stats') }}
    group by team_name
),

final_summary as (
    select
        s.team_name,
        
        -- Estatísticas da equipe
        s.total_players,
        s.total_goals,
        s.total_assists,
        s.total_goal_contributions,
        round(s.avg_age, 1) as avg_age,
        s.total_minutes,
        s.total_yellow_cards,
        s.total_red_cards,
        round(s.avg_expected_goals, 2) as avg_expected_goals_per_player,
        round(s.avg_expected_assists, 2) as avg_expected_assists_per_player,
        
        -- Composição por posição
        p.goalkeepers,
        p.defenders,
        p.midfielders,
        p.attackers,
        
        -- Informações financeiras
        m.total_squad_value_euros,
        round(cast(m.total_squad_value_euros as float64) / 1000000, 2) as total_squad_value_millions_eur,
        round(cast(m.avg_player_value_euros as float64) / 1000000, 2) as avg_player_value_millions_eur,
        round(cast(m.highest_valued_player_euros as float64) / 1000000, 2) as highest_valued_player_millions_eur,
        m.players_expiring_soon,
        m.very_high_value_players,
        
        -- Métricas calculadas
        round(cast(s.total_goals as float64) / s.total_players, 2) as goals_per_player,
        round(cast(s.total_assists as float64) / s.total_players, 2) as assists_per_player,
        round(cast(s.total_goal_contributions as float64) / s.total_players, 2) as goal_contributions_per_player,
        
        -- Classificação da equipe
        case 
            when s.total_goals >= 80 then 'High Scoring'
            when s.total_goals >= 60 then 'Good Scoring'
            when s.total_goals >= 40 then 'Average Scoring'
            else 'Low Scoring'
        end as team_scoring_classification,
        
        case 
            when m.total_squad_value_euros >= 200000000 then 'Very Expensive Squad'
            when m.total_squad_value_euros >= 150000000 then 'Expensive Squad'
            when m.total_squad_value_euros >= 100000000 then 'Moderate Squad'
            else 'Budget Squad'
        end as squad_value_classification,
        
        current_timestamp() as processed_at
        
    from team_stats s
    left join team_market m on s.team_name = m.team_name
    left join team_positions p on s.team_name = p.team_name
)

select * from final_summary
order by total_squad_value_euros desc
