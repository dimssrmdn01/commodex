
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        asset_id, date_key
    from "neondb"."public"."fct_harga_harian"
    group by asset_id, date_key
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test