## 📂 Estructura del Proyecto

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
├── docs/                              # Project diagrams and technical documentation
│   ├── architecture.png
│   ├── pipeline_flow.png
│   ├── data_model.png
│   └── ...
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
├── .gitignore                         # Temporary files, credentials, and local data excluded from Git
├── Dockerfile                         # Container configuration for Cloud Run Jobs
├── README.md                          # Main project documentation and usage guide
├── requirements.txt                   # Python project dependencies
└── main.py                            # Main entry point and pipeline orchestrator
```
