"""Commodex dashboard: membaca layer Silver dan Gold dari Neon (read-only)."""

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

import styling
from styling import THEME

st.set_page_config(page_title="Commodex", page_icon="🪙", layout="wide")
styling.inject_css()

ASSET_LABELS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "tether": "Tether",
    "solana": "Solana",
    "binancecoin": "BNB",
}
TZ = "Asia/Jakarta"


# ---------- koneksi & data ----------
@st.cache_resource
def get_engine():
    cfg = st.secrets["db"]  # hanya dari secrets, bukan .env milik owner
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg.get("port", 5432)),
        database=cfg["name"],
        query={"sslmode": cfg.get("sslmode", "require")},
    )
    return create_engine(url, pool_pre_ping=True)


def run_query(sql: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


@st.cache_data(ttl=600, show_spinner="Mengambil data dari Neon...")
def load_prices() -> pd.DataFrame:
    df = run_query(
        """
        select asset_id, price_idr, price_usd, change_24h_pct,
               last_updated_at, ingested_at
        from public.stg_harga_pasar
        order by last_updated_at
        """
    )
    df["last_updated_at"] = pd.to_datetime(df["last_updated_at"], utc=True).dt.tz_convert(TZ)
    return df


@st.cache_data(ttl=600, show_spinner=False)
def load_daily() -> pd.DataFrame:
    return run_query(
        """
        select asset_id, date_key, avg_price_idr, avg_price_usd,
               max_change_24h_pct, total_datapoints
        from public.fct_harga_harian
        order by date_key desc, asset_id
        """
    )


def fmt_price(value: float, currency: str) -> str:
    if currency == "IDR":
        return f"Rp {value:,.0f}"
    return f"${value:,.4f}" if value < 10 else f"${value:,.2f}"


# ---------- muat data ----------
prices, daily, load_error = None, None, None
try:
    prices, daily = load_prices(), load_daily()
except Exception as exc:
    load_error = type(exc).__name__

status = None
if prices is not None and not prices.empty:
    status = f"Pipeline online &nbsp;|&nbsp; data terakhir {prices['last_updated_at'].max().strftime('%d %b %H:%M')} WIB"

styling.hero(
    "Commodex",
    "Harga aset dari CoinGecko, diproses lewat Bronze, Silver, dan Gold di PostgreSQL (Neon).",
    status,
)

if load_error:
    st.error("Tidak bisa mengambil data dari database. Periksa konfigurasi secrets.")
    st.caption(f"Detail teknis: {load_error}")
    st.stop()
if prices.empty:
    st.info("Belum ada data di layer Silver. Jalankan pipeline terlebih dahulu.")
    st.stop()

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("**Filter**")
    asset = st.selectbox("Aset", list(ASSET_LABELS), format_func=lambda a: ASSET_LABELS.get(a, a))
    currency = st.radio("Mata uang", ["IDR", "USD"], horizontal=True)
    st.divider()
    st.caption("Data di-cache 10 menit.")
    if st.button("Muat ulang data"):
        st.cache_data.clear()
        st.rerun()

price_col = f"price_{currency.lower()}"
asset_df = prices[prices["asset_id"] == asset]
if asset_df.empty:
    st.warning(f"Belum ada data untuk {ASSET_LABELS[asset]}.")
    st.stop()
latest = asset_df.iloc[-1]

# ---------- KPI ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    f"Harga terakhir ({currency})",
    fmt_price(latest[price_col], currency),
    delta=f"{latest['change_24h_pct']:+.2f}% (24 jam)",
)
c2.metric("Jumlah snapshot", f"{len(asset_df):,}")
c3.metric("Data pertama", asset_df["last_updated_at"].min().strftime("%d %b %Y"))
c4.metric("Update terakhir (WIB)", latest["last_updated_at"].strftime("%d %b %H:%M"))

st.markdown("<br>", unsafe_allow_html=True)
tab_price, tab_daily, tab_all = st.tabs(["Harga", "Ringkasan harian", "Semua aset"])

with tab_price:
    fig = px.area(
        asset_df,
        x="last_updated_at",
        y=price_col,
        labels={"last_updated_at": "Waktu (WIB)", price_col: f"Harga ({currency})"},
        title=f"Harga {ASSET_LABELS[asset]} dari waktu ke waktu",
    )
    fig.update_traces(
        line=dict(color=THEME["gold"], width=3),
        fillcolor="rgba(255,216,102,0.10)",
        mode="lines+markers",
        marker=dict(size=6, color=THEME["gold"]),
    )
    lo, hi = asset_df[price_col].min(), asset_df[price_col].max()
    pad = (hi - lo) * 0.15 or hi * 0.01
    fig = styling.style_fig(fig)
    fig.update_yaxes(range=[lo - pad, hi + pad])
    st.plotly_chart(fig, use_container_width=True)
    if len(asset_df) < 10:
        st.caption("Grafik masih pendek karena histori baru mulai terkumpul. Pipeline menambah snapshot setiap hari.")

with tab_daily:
    st.caption("Tabel Gold `fct_harga_harian`: satu baris per aset per hari.")
    st.dataframe(
        daily[daily["asset_id"] == asset],
        hide_index=True,
        use_container_width=True,
        column_config={
            "asset_id": "Aset",
            "date_key": "Tanggal",
            "avg_price_idr": st.column_config.NumberColumn("Rata-rata (IDR)", format="Rp %.0f"),
            "avg_price_usd": st.column_config.NumberColumn("Rata-rata (USD)", format="$%.4f"),
            "max_change_24h_pct": st.column_config.NumberColumn("Perubahan 24j maks (%)", format="%.2f"),
            "total_datapoints": "Jumlah datapoint",
        },
    )

with tab_all:
    st.caption("Snapshot terbaru untuk semua aset.")
    latest_all = prices.sort_values("last_updated_at").groupby("asset_id").tail(1).copy()
    latest_all["Aset"] = latest_all["asset_id"].map(ASSET_LABELS).fillna(latest_all["asset_id"])
    latest_all["Waktu (WIB)"] = latest_all["last_updated_at"].dt.strftime("%d %b %Y %H:%M")
    latest_all = latest_all.rename(
        columns={"price_idr": "Harga (IDR)", "price_usd": "Harga (USD)", "change_24h_pct": "Perubahan 24j (%)"}
    )
    st.dataframe(
        latest_all[["Aset", "Harga (IDR)", "Harga (USD)", "Perubahan 24j (%)", "Waktu (WIB)"]],
        hide_index=True,
        use_container_width=True,
    )

with st.expander("Tentang data ini"):
    st.markdown(
        "- **Sumber:** CoinGecko API.\n"
        "- **Silver (`stg_harga_pasar`):** data bersih dan terdeduplikasi, untuk grafik harga.\n"
        "- **Gold (`fct_harga_harian`):** agregasi harian per aset.\n"
        "- **Akses:** dashboard memakai user database read-only.\n"
        "- Bukan saran investasi."
    )