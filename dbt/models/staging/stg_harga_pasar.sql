with raw_data as (
    select * from {{ source('bronze', 'bronze_harga_pasar') }}
)

select
    asset_id,
    price_idr::numeric as price_idr,
    price_usd::numeric as price_usd,
    round(change_24h_idr::numeric, 2) as change_24h_pct,
    to_timestamp(last_updated_timestamp) as last_updated_at,
    ingested_at::timestamp as ingested_at
from raw_data
