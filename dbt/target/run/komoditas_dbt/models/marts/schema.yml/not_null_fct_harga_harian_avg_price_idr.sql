
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select avg_price_idr
from "komoditas_db"."public"."fct_harga_harian"
where avg_price_idr is null



  
  
      
    ) dbt_internal_test