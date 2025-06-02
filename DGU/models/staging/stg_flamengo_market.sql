{{ config(materialized='view') }}

with source_data as (
    select * from {{ ref('flamengo_tabela_0_mercado') }}
),

cleaned_data as (
    select
        -- Identificadores
        player as player_name,
        position as position_detailed,
        time as team_name,
        
        -- Informações básicas
        age,
        nationality,
        
        -- Informações financeiras
        `market_value_eur` as market_value_euros,
        `contract_expires` as contract_expiry_date,

        -- Metadados
        `data_extracao` as extraction_date,
        fonte as source_url,
        
        -- Campos calculados
        case
            when `contract_expires` <= '2025-12-31' then 'Expiring Soon'
            when `contract_expires` <= '2026-12-31' then 'Medium Term'
            else 'Long Term'
        end as contract_status,

        case
            when `market_value_eur` >= 20000000 then 'Very High'
            when `market_value_eur` >= 10000000 then 'High'
            when `market_value_eur` >= 5000000 then 'Medium'
            when `market_value_eur` >= 1000000 then 'Low'
            else 'Very Low'
        end as market_value_category,

        -- Conversão para milhões para facilitar leitura
        round(cast(`market_value_eur` as float64) / 1000000, 2) as market_value_millions_eur
        
    from source_data
)

select * from cleaned_data
