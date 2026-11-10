
  
    

  create  table "neondb"."public"."fct_harga_harian__dbt_tmp"
  
  
    as
  
  (
    with silver_data as (
    select * from "neondb"."public"."stg_harga_pasar"
)

select
    asset_id,
    date(last_updated_at) as date_key,
    round(avg(price_idr), 2) as avg_price_idr,
    round(avg(price_usd), 2) as avg_price_usd,
    max(change_24h_pct) as max_change_24h_pct,
    count(*) as total_datapoints
from silver_data
group by 1, 2
  );
  