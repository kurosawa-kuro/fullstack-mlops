{{
  config(
    materialized='table',
    schema='bronze'
  )
}}

-- Bronze layer: Raw house data from ingestion
-- This model references the raw data ingested by the Python ingestion process
SELECT 
    id,
    price,
    sqft,
    bedrooms,
    bathrooms,
    location,
    year_built,
    condition,
    created_at
FROM {{ source('raw', 'bronze_raw_house_data') }} 