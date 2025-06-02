{{ config(materialized='table') }}

-- Teste simples para verificar se o mart funciona
select 
    'teste' as status,
    current_timestamp() as created_at
