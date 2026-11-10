<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&pause=1000&color=2DD4BF&center=true&vCenter=true&width=700&lines=COMMODEX;Medallion+Data+Pipeline;Bronze+%E2%86%92+Silver+%E2%86%92+Gold;Python+%C2%B7+PostgreSQL+%C2%B7+dbt+%C2%B7+GitHub+Actions" alt="Typing SVG" />
</div>

<div align="center">

[![Pipeline](https://img.shields.io/github/actions/workflow/status/dimssrmdn01/commodex/pipeline.yml?style=for-the-badge&label=Pipeline&logo=githubactions&logoColor=2DD4BF&labelColor=0f172a)](https://github.com/dimssrmdn01/commodex/actions/workflows/pipeline.yml)
![Python](https://img.shields.io/badge/Python-3.11-0f172a?style=for-the-badge&logo=python&logoColor=2DD4BF)
![dbt](https://img.shields.io/badge/dbt-1.12-0f172a?style=for-the-badge&logo=dbt&logoColor=FF694A)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-0f172a?style=for-the-badge&logo=postgresql&logoColor=60A5FA)
![License](https://img.shields.io/badge/License-MIT-0f172a?style=for-the-badge&logoColor=2DD4BF)

</div>

## About The Project

**Commodex** adalah pipeline *end-to-end analytics engineering* yang menerapkan **Medallion Architecture** (Bronze → Silver → Gold). Data harga aset diambil dari [CoinGecko API](https://www.coingecko.com/en/api), dibersihkan dan dimodelkan dengan dbt, lalu divalidasi dengan data quality test yang berjalan otomatis lewat GitHub Actions.

**Key highlights:**
- **Layered by design.** Bronze menyimpan data mentah apa adanya, Silver membersihkan dan mendeduplikasi, Gold menyajikan agregasi siap analisis.
- **Tested, not assumed.** 7 tes dbt (`not_null`, `accepted_values`, `unique_combination_of_columns`) dijalankan di setiap eksekusi.
- **Fail-fast CI.** Jika ingestion gagal, pipeline langsung berhenti dan workflow berstatus merah.
- **Reproducible.** Satu `docker compose up` untuk database lokal, versi dependency dikunci.

**Aset yang dilacak:** Bitcoin, Ethereum, Tether, Solana, BNB (harga IDR dan USD).

## Architecture

````mermaid
flowchart TD
    A[CoinGecko API] -->|Python + pandas| B[(Bronze<br/>bronze_harga_pasar)]
    B -->|dbt staging| C[(Silver<br/>stg_harga_pasar)]
    C -->|dbt mart| D[(Gold<br/>fct_harga_harian)]
    D --> E[dbt tests]
    F[GitHub Actions<br/>push · PR · cron harian] -.->|orchestrates| A
````

## Data Layers

| Layer | Tipe | Objek | Deskripsi |
| :--- | :--- | :--- | :--- |
| Bronze | Table | `bronze_harga_pasar` | Snapshot mentah API (append-only) + `ingested_at` |
| Silver | View | `stg_harga_pasar` | Casting numerik, epoch → timestamp, deduplikasi per `asset_id` + `last_updated_timestamp` |
| Gold | Table | `fct_harga_harian` | Per aset per hari: rata-rata harga IDR/USD, perubahan 24 jam maksimum, jumlah datapoint |

## Data Quality Tests

| Model | Kolom | Tes |
| :--- | :--- | :--- |
| `stg_harga_pasar` | `asset_id` | `not_null`, `accepted_values` |
| `stg_harga_pasar` | `last_updated_at` | `not_null` |
| `fct_harga_harian` | `asset_id`, `date_key`, `avg_price_idr` | `not_null` |
| `fct_harga_harian` | `asset_id` + `date_key` | `unique_combination_of_columns` |

## Tech Stack

| Layer | Tools & Technologies |
| :--- | :--- |
| Ingestion | Python 3.11, requests, pandas, SQLAlchemy |
| Storage | PostgreSQL 15 (Docker Compose lokal, service container di CI) |
| Transformation | dbt-core 1.12, dbt-postgres 1.11, dbt_utils |
| CI/CD | GitHub Actions (push, pull request, cron harian 00:00 UTC, manual) |

## Project Structure

````text
commodex/
├── .github/workflows/pipeline.yml   # CI/CD
├── dbt/                             # models, tests, packages.yml
├── src/ingest.py                    # ingestion ke Bronze
├── docker-compose.yml               # PostgreSQL lokal
├── requirements.txt
├── LICENSE
└── README.md
````

## Getting Started

**Prerequisites:** Python 3.11, Docker.

**1. Clone dan setup environment**
````bash
git clone https://github.com/dimssrmdn01/commodex.git
cd commodex
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
````

**2. Jalankan PostgreSQL lokal**
````bash
docker compose up -d
````

**3. Ingest dan transformasi**
````bash
python src/ingest.py
cd dbt
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
````

Kredensial database bisa diatur lewat environment variable `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (default untuk development lokal).

## Example Query

````sql
SELECT asset_id, date_key, avg_price_usd, max_change_24h_pct, total_datapoints
FROM public.fct_harga_harian
ORDER BY date_key DESC, asset_id;
````

## Known Limitations

- Database di CI bersifat sementara, sehingga histori harga tidak tersimpan antar-run.
- Ingestion berupa snapshot per eksekusi (batch), bukan streaming.
- Sumber data saat ini hanya aset kripto.

## Roadmap

- [ ] Database cloud persisten (Neon/Supabase) + GitHub Secrets untuk akumulasi histori
- [ ] Tambah sumber komoditas riil (emas, minyak)
- [ ] Dashboard (Streamlit) di atas layer Gold
- [ ] dbt docs + lineage graph via GitHub Pages

## Author

Built by **Dimas Arya Ramadhan** - Undergraduate Data Science student at ITERA.

## License

MIT License.