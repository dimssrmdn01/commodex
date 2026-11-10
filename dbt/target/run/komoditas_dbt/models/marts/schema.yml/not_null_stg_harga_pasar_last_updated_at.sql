
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select last_updated_at
from "komoditas_db"."public"."stg_harga_pasar"
where last_updated_at is null



  
  
      
    ) dbt_internal_test