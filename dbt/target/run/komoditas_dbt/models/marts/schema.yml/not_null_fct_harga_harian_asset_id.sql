
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select asset_id
from "komoditas_db"."public"."fct_harga_harian"
where asset_id is null



  
  
      
    ) dbt_internal_test