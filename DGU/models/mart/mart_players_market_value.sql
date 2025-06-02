{{ config(materialized='table') }}

with all_teams_market as (
    -- União de todos os valores de mercado dos times
    select * from {{ ref('stg_palmeiras_market') }}
    union all
    select * from {{ ref('stg_flamengo_market') }}
    union all
    select * from {{ ref('stg_corinthians_market') }}
),

final_market as (
    select
        -- Identificadores únicos
        concat(team_name, '_', player_name) as player_id,
        player_name,
        team_name,
        position_detailed,
        age,
        nationality,
        
        -- Informações financeiras
        market_value_euros,
        market_value_millions_eur,
        market_value_category,
        
        -- Informações contratuais
        contract_expiry_date,
        contract_status,
        
        -- Análises de idade vs valor
        case 
            when age <= 21 and market_value_millions_eur >= 10 then 'Young Talent'
            when age <= 25 and market_value_millions_eur >= 15 then 'Prime Prospect'
            when age <= 28 and market_value_millions_eur >= 20 then 'Peak Value'
            when age <= 32 and market_value_millions_eur >= 10 then 'Experienced Star'
            when age > 32 and market_value_millions_eur >= 5 then 'Veteran Value'
            else 'Standard Player'
        end as player_value_profile,
        
        -- Tempo restante de contrato em anos
        date_diff(date(contract_expiry_date), current_date(), year) as contract_years_remaining,
        
        -- Valor por ano de idade (indicador de potencial)
        round(market_value_millions_eur / age, 2) as value_per_age_ratio,
        
        -- Metadados
        extraction_date,
        source_url,
        current_timestamp() as processed_at
        
    from all_teams_market
    where player_name is not null
)

select * from final_market
order by market_value_euros desc, team_name
