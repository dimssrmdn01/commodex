
    
    

with all_values as (

    select
        asset_id as value_field,
        count(*) as n_records

    from "neondb"."public"."stg_harga_pasar"
    group by asset_id

)

select *
from all_values
where value_field not in (
    'bitcoin','ethereum','tether','solana','binancecoin'
)


