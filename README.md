# Industrial Maintenance Data Pipeline

End-to-end data engineering pipeline for processing industrial production, maintenance, and quality data from heterogeneous sources and generating analytical datasets on Google Cloud Platform.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GCP](https://img.shields.io/badge/GCP-Cloud_Run_%7C_BigQuery-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## 1. Business Context & 7-Day Scenario

This project simulates a **7-day data workflow for an industrial maintenance company**, centralizing operational data related to production, maintenance, and quality. Data is initially processed from PostgreSQL, while on **Day 4**, an external SFTP source is introduced to integrate third-party quality control data into the existing pipeline.

```text
                         7-DAY PIPELINE EXECUTION FLOW

                                        Days 4–7: SFTP
                                       (Manual / Local)
                                              │
                                         IMPORT DATA
                                              │
                                              ▼
INSERT / BULK INSERT ───→ PostgreSQL ───→  Bronze  ───→ Transform + DQ ───→  Silver  ───→  BigQuery ───→ Gold ───→ Looker
     (Days 1–7)                           CSV | GCS         Pandas        Parquet | GCS               SQL

• Orchestration: Cloud Scheduler · Cloud Run Jobs
• Cloud: GCS · BigQuery · Artifact Registry · Secret Manager · IAM
• Quality & Ops: Data Quality · Pytest · GitHub Actions · Logging · Monitoring
• Strategy: Full Refresh · Medallion Architecture
```

The scenario demonstrates how an existing batch pipeline can incorporate a **new heterogeneous data source** while preserving the same transformation, validation, storage, and analytical workflow.

---

## 2. Architecture & Data Flow

<img width="1197" height="798" alt="Medallion architecture data flow diagram" src="https://github.com/user-attachments/assets/86aa229a-d1e1-4998-8f76-0dd58f23721b" />

The pipeline follows a strict **Medallion Architecture**, decoupling extraction, transformation, and analytical modeling:

- **Ingestion:** PostgreSQL and SFTP sources are extracted into **Google Cloud Storage**, preserving raw CSV files alongside JSON metadata for traceability, auditing, and historical reproducibility.
- **Transformation:** **Pandas-based transformations** perform schema normalization, data cleansing, type standardization, and data quality validation. Processed datasets are serialized as **Parquet** and stored in the Silver layer.
- **Analytics:** **BigQuery SQL models** consume the Silver layer to build curated **Gold** datasets optimized for analytical workloads and reporting.

> **Note on SFTP execution:** the PostgreSQL extraction and Gold layer build run fully automated on Cloud Run, but the **SFTP extraction step currently requires manual/local execution** — see [Section 3.1](#31-known-limitation-sftp-execution) for details.

---

## 3. Cloud Infrastructure & Engineering Practices

The pipeline is containerized and designed for scalable cloud execution.

| Service               | Purpose                                                   |
| :--------------------- | :--------------------------------------------------------- |
| **Cloud Run Jobs**    | Containerized batch ETL execution                         |
| **Cloud Storage**     | Immutable Bronze and optimized Silver (Parquet) storage    |
| **BigQuery**          | Analytical Data Warehouse and Gold layer materialization   |
| **Artifact Registry** | Secure Docker image storage                                |
| **Secret Manager**    | Environment and credential management                      |

**Core Engineering Practices:**

- **Decoupled Logic:** Python handles ETL; SQL handles business KPIs.
- **CI & Testing:** Automated testing with Pytest and GitHub Actions.
- **Hybrid Ingestion:** Standardizes heterogeneous data sources, seamlessly unifying internal relational database streams (PostgreSQL) with remote external vendor files (SFTP) into a single processing engine.
- **Idempotent Execution:** The pipeline is designed to be safely executed multiple times for the same logical date without duplicating downstream data, ensuring a reliable state in the data warehouse.
- **Backfilling:** Custom CLI tools (`trigger_backfilling.py`) allow surgical historical reprocessing.

### 3.1 Known limitation: SFTP execution

The PostgreSQL-to-Gold flow runs fully automated on Cloud Run. The SFTP step (`src/extractors/sftp_extractor.py`), however, must be **triggered manually from a local environment**: the SFTP server (SFTPGo) is hosted on `localhost`, which Cloud Run can't reach — an infra limitation, not a code issue.

Until SFTPGo is deployed somewhere network-accessible, run `python main.py` locally to pull the external file (`quality_control_day4.csv`) into Bronze. From there, transformation and BigQuery loading proceed the same way regardless of source.

**Planned fix:** move SFTPGo to a public/VPC-reachable host so this step can run inside Cloud Run.

---

## 4. Data Quality & Reliability

Data is validated *before* reaching the analytical layers using a fail-fast approach.

<img width="1411" height="371" alt="image" src="https://github.com/user-attachments/assets/722cabfb-c215-47df-82f7-99cf54a8b1a6" />

- **Schema & Constraints:** Ensures exact column matches, non-empty datasets, and uniqueness of primary keys.
- **Business Rules:** Validates that metrics (costs, quantities) are positive and checks chronological consistency (e.g., `downtime.start_timestamp < downtime.end_timestamp`).
- **Pipeline State:** If a critical validation fails, the specific table is dropped from the current run, but the overall pipeline gracefully continues with the remaining tables, flagging a final exit error for monitoring tools.

---

## 5. Testing

The pipeline includes automated unit tests covering data cleaning functions, quality validations, and transformation logic, run via **Pytest** and integrated into the CI workflow (GitHub Actions) on every push and pull request.

<img width="1456" height="656" alt="pytest results" src="https://github.com/user-attachments/assets/bdd39d9b-28db-40fb-8564-5660fcf04137" />

*Test suite covering cleaning rules, schema validation, and business logic across all Silver-layer tables.*

Run locally with:

```bash
pytest -v
```

---

## 6. FAQ & Design Decisions

- **Why use Cloud Run Jobs instead of Cloud Functions?**

  The ETL pipeline is a finite, scheduled batch workload that processes multiple tables sequentially. **Cloud Run Jobs** are better suited for run-to-completion workloads, allowing the entire pipeline to run as a containerized application with configurable CPU, memory, and execution time. Cloud Functions would be more appropriate for isolated, event-driven tasks rather than a multi-stage ETL process.

- **Why use Supabase (PostgreSQL) instead of Google Cloud SQL?**

  The decision was driven by cost and connectivity constraints. Running PostgreSQL locally introduced connectivity issues in this environment, making it unreliable as a pipeline source, while Google Cloud SQL was avoided to prevent additional infrastructure costs. Supabase provided a free, managed PostgreSQL environment that solved both problems.

- **Why implement a Full Refresh loading strategy?**

  For datasets processing fewer than 100k records per run, a Full Refresh strategy (truncating and reloading the destination tables) is efficient, simple to maintain, and eliminates the risk of data duplication or state mismatch. Given the current data volume and workload characteristics, the additional complexity of incremental loading was not justified.

- **Why integrate an external SFTP server into the pipeline?**

  Industrial environments rarely rely on a single centralized data source. Third-party vendors, external laboratories, and legacy systems often exchange operational data through flat files and SFTP. Integrating SFTP demonstrates the pipeline's ability to ingest heterogeneous data sources and unify them into a single processing architecture.

---

## 7. Analytical Outputs (Gold Layer)

The final layer provides curated analytical outputs designed to answer specific business questions, with tables ready for consumption in Looker Studio.

<details>
<summary><b>🔍 View SQL Model: Daily Plant Performance</b></summary>

```sql
CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_plant_performance` AS
SELECT
    DATE(y.execution_date) AS production_date,
    p.plant_name AS plant,
    p.region AS region,
    SUM(y.good_quantity) AS good_units,
    SUM(y.scrap_quantity) AS rejected_units,
    ROUND(SAFE_DIVIDE(SUM(y.good_quantity), SUM(y.good_quantity + y.scrap_quantity)) * 100, 2) AS quality_percentage
FROM `industrial-data-pipeline.industrial_silver.production_yields` AS y
JOIN `industrial-data-pipeline.industrial_silver.machines` AS m
    ON y.machine_id = m.machine_id
JOIN `industrial-data-pipeline.industrial_silver.plants` AS p
    ON m.plant_id = p.plant_id
GROUP BY
    production_date,
    plant,
    region
ORDER BY
    production_date DESC,
    plant ASC;
```

</details>

<img width="871" height="421" alt="performance" src="https://github.com/user-attachments/assets/83a9da45-b8a1-4888-942f-6fb292be0870" />

*Daily production performance by plant and region. The quality rate represents the percentage of good units relative to total production volume (good + rejected).*

---

### Other Gold Datasets

| Dataset                     | Description                                                                |
| :--------------------------- | :--------------------------------------------------------------------------- |
| `gold_daily_production`     | Daily production volume and cost by plant and product.                    |
| `gold_machine_downtime`     | Maintenance KPIs detailing lost minutes by plant, machine, and failure reason. |
| `gold_material_consumption` | Logistics tracing material consumption by product and supplier.           |
| `gold_plant_performance`    | Executive summary of production quality and scrap percentages by region.  |
| `gold_quality_performance`  | Quality control performance by plant.                                     |

### Dashboard & Visualization

The `gold_plant_performance` table feeds a **Looker Studio** dashboard that consolidates production and quality KPIs across all plants, with filtering by period, region, and plant.

<img width="1152" height="866" alt="Industrial Operations Dashboard" src="https://github.com/user-attachments/assets/a673f8fc-a168-4a6c-8b69-9bb8f5e395c0" />

*Industrial Operations Dashboard — daily quality trend, plant performance ranking, and a breakdown table of good/rejected units by plant and region.*

**Key metrics displayed:**

- **Good Units / Rejected Units:** total production volume split by outcome.
- **Quality Percentage:** good units as a share of total production, consistent with the `quality_percentage` KPI computed in `gold_plant_performance`.
- **Inspection Approval % (5 Days):** rolling approval rate from quality control inspections.
- **Daily Quality Trend:** quality percentage over time, used to spot degradation early.
- **Plant Performance Ranking:** plants sorted by quality percentage, to quickly flag underperformers.
  
---

## 8. Getting Started

### Prerequisites

- Python 3.12+
- Google Cloud project with a Service Account (BigQuery + Cloud Storage access)
- PostgreSQL (Supabase) source database
- SFTP server access

### Installation

```bash
git clone https://github.com/benjaminjorq/industrial-maintenance-pipeline.git
cd industrial-maintenance-pipeline

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with your database, GCP, and SFTP credentials (see `.env.example` for the required variables).

> Make sure `known_hosts` is present in the project root — it's required for the SFTP connection (`RejectPolicy`).

> **Tech note:** the Cloud Run job and the SFTP connection currently run separately. The SFTP server (SFTPGo) is hosted on `localhost`, so it isn't reachable from within the Cloud Run environment — this is a known infra limitation, not a code issue. Until SFTPGo is deployed somewhere network-accessible to Cloud Run (e.g. a public/VPC-reachable host), the SFTP extraction step needs to be triggered locally.

### Run the pipeline

```bash
python main.py
```

Runs the full flow: extraction (PostgreSQL + SFTP) → Silver transformation & validation → BigQuery load → Gold layer build.
> When run locally, this command extracts from **both** PostgreSQL and SFTP. When deployed on Cloud Run, only the PostgreSQL-sourced tables and the Gold layer build execute automatically — the SFTP-sourced table (`quality_control`) must be extracted in a separate local run beforehand (see [Section 3.1](#31-known-limitation-sftp-execution)).

### Backfill & Tests

```bash
python backfill/trigger_backfilling.py   # reprocess specific tables/dates
pytest -v                                # run tests
```

### Run with Docker (optional)

```bash
docker build -t industrial-maintenance-pipeline .
docker run --env-file .env industrial-maintenance-pipeline
```

---

## 9. Project Structure

```text
industrial-maintenance-pipeline/
│
├── .github/
│   └── workflows/
│       └── ci.yml                     # Automated tests and validations with GitHub Actions
│
├── backfill/
│   └── trigger_backfilling.py         # Runs historical reprocessing for specific dates
│
├── data/                              # Temporary local development storage (Excluded from Git)
│   ├── bronze/                        # Raw extracted data without transformations (CSV)
│   │   ├── plants/
│   │   │   └── ingestion_date=YYYY-MM-DD/
│   │   │       └── plants_YYYY-MM-DD.csv
│   │   ├── machines/
│   │   ├── production_orders/
│   │   ├── production_yields/
│   │   └── ...
│   │
│   └── silver/                        # Cleaned and standardized data in Parquet format
│       ├── plants/
│       │   └── ingestion_date=YYYY-MM-DD/
│       │       └── plants_YYYY-MM-DD.parquet
│       ├── machines/
│       ├── production_orders/
│       ├── production_yields/
│       └── ...
│
│
├── sql/
│   ├── plants.sql                     # SQL queries for extraction from PostgreSQL
│   ├── machines.sql
│   ├── products.sql
│   ├── production_orders.sql
│   ├── production_yields.sql
│   ├── ...
│   │
│   └── gold/
│       ├── gold_daily_production.sql  # Analytical models for the Gold layer
│       ├── gold_machine_downtime.sql
│       ├── gold_material_consumption.sql
│       ├── gold_plant_performance.sql
│       └── gold_quality_performance.sql
│
├── src/                               # Source code for the ETL pipeline
│   ├── config/
│   │   └── settings.py                # Configuration and environment variable management
│   │
│   ├── database/
│   │   └── connection.py              # PostgreSQL connection management
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── postgres_extractor.py      # Extracts data from PostgreSQL into Bronze
│   │   └── sftp_extractor.py          # Extracts CSV files through SFTP
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── data_cleaning_functions.py # Reusable data cleaning and standardization functions
│   │   └── transformer.py             # Orchestrates Bronze-to-Silver transformations
│   │
│   ├── load/
│   │   ├── bigquery_loader.py         # Loads Parquet data from Silver into BigQuery
│   │   └── gold_loader.py             # Executes SQL models for the Gold layer
│   │
│   └── validations/
│       └── data_quality.py            # Validates schemas, nulls, uniqueness, and business rules
│
├── tests/                             # Automated tests with pytest
│   ├── conftest.py                    # Shared fixtures and test data
│   ├── test_transformer.py            # Transformation process tests
│   ├── test_data_cleaning.py          # Data cleaning function tests
│   ├── test_data_quality.py           # Data quality validation tests
│   └── ...
│
├── utils/
│   └── gcs_uploader.py                # Utility functions for Google Cloud Storage
│
├── .dockerignore                      # Files excluded from the Docker image build
├── .env.example                       # Environment variable template
└── .gitignore                         # Temporary files, credentials, and virtual enviroments
