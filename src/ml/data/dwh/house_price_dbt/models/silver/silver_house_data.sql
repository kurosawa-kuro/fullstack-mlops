{{
  config(
    materialized='table',
    schema='silver'
  )
}}

-- Silver layer: Cleaned and standardized house data
-- This model performs data cleaning, validation, and standardization

WITH cleaned_data AS (
  SELECT 
    id,
    price,
    sqft,
    bedrooms,
    bathrooms,
    location,
    year_built,
    condition,
    created_at,
    
    -- Data validation and cleaning
    CASE 
      WHEN price > 0 THEN price 
      ELSE NULL 
    END as cleaned_price,
    
    CASE 
      WHEN sqft > 0 THEN sqft 
      ELSE NULL 
    END as cleaned_sqft,
    
    CASE 
      WHEN bedrooms > 0 THEN bedrooms 
      ELSE NULL 
    END as cleaned_bedrooms,
    
    CASE 
      WHEN bathrooms > 0 THEN bathrooms 
      ELSE NULL 
    END as cleaned_bathrooms,
    
    CASE 
      WHEN year_built >= 1900 AND year_built <= EXTRACT(YEAR FROM CURRENT_DATE) 
      THEN year_built 
      ELSE NULL 
    END as cleaned_year_built,
    
    -- Standardize location names
    TRIM(UPPER(location)) as cleaned_location,
    
    -- Standardize condition values
    TRIM(UPPER(condition)) as cleaned_condition,
    
    -- Calculate derived fields
    CASE 
      WHEN price > 0 AND sqft > 0 THEN price / sqft 
      ELSE NULL 
    END as price_per_sqft,
    
    CASE 
      WHEN year_built > 0 THEN EXTRACT(YEAR FROM CURRENT_DATE) - year_built 
      ELSE NULL 
    END as house_age,
    
    CASE 
      WHEN bedrooms > 0 AND bathrooms > 0 THEN bedrooms / bathrooms 
      ELSE NULL 
    END as bed_bath_ratio
    
  FROM {{ ref('bronze_raw_house_data') }}
),

final_data AS (
  SELECT 
    id,
    cleaned_price as price,
    cleaned_sqft as sqft,
    cleaned_bedrooms as bedrooms,
    cleaned_bathrooms as bathrooms,
    cleaned_location as location,
    cleaned_year_built as year_built,
    cleaned_condition as condition,
    price_per_sqft,
    house_age,
    bed_bath_ratio,
    created_at,
    
    -- Data quality flags
    CASE 
      WHEN cleaned_price IS NOT NULL 
        AND cleaned_sqft IS NOT NULL 
        AND cleaned_bedrooms IS NOT NULL 
        AND cleaned_bathrooms IS NOT NULL 
        AND cleaned_year_built IS NOT NULL 
        AND cleaned_location IS NOT NULL 
        AND cleaned_condition IS NOT NULL 
      THEN TRUE 
      ELSE FALSE 
    END as is_complete_record,
    
    -- Outlier detection
    CASE 
      WHEN price_per_sqft > 1000 OR price_per_sqft < 50 THEN TRUE 
      ELSE FALSE 
    END as is_price_outlier,
    
    CASE 
      WHEN house_age > 100 OR house_age < 0 THEN TRUE 
      ELSE FALSE 
    END as is_age_outlier
    
  FROM cleaned_data
)

SELECT * FROM final_data 