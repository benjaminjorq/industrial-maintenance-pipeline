## 📂 Estructura del Proyecto (En desarrollo)

```text
industrial-maintenance-pipeline/
│
├── .github/
│   └── workflows/
│       └── ci.yml                     # Pipeline de Integración Continua (Próximamente)
│
├── backfill/
│   └── trigger_backfilling.py         # Ejecuta cargas históricas para reprocesar fechas específicas
│
├── data/                              # Almacenamiento temporal utilizado durante el desarrollo local (Ignorado por Git)
│   ├── bronze/                        # Datos extraídos sin transformaciones (Formato CSV)
│   │   ├── plants/
│   │   │   └── ingestion_date=YYYY-MM-DD/
│   │   │       └── plants_YYYY-MM-DD.csv
│   │   ├── machines/
│   │   ├── production_orders/
│   │   ├── production_yields/
│   │   └── ...
│   │
│   └── silver/                        # Datos limpios y estandarizados en formato columnar Parquet
│       ├── plants/
│       │   └── ingestion_date=YYYY-MM-DD/
│       │       └── plants_YYYY-MM-DD.parquet
│       ├── machines/
│       ├── production_orders/
│       ├── production_yields/
│       └── ...
│
├── docs/                              # Diagramas de arquitectura, modelo de datos y documentación técnica (Proximamente)
│   ├── architecture.png
│   ├── pipeline_flow.png
│   ├── data_model.png
│   └── ...
│
├── sql/
│   ├── plants.sql                     # Consultas SQL utilizadas para extraer datos desde PostgreSQL
│   ├── machines.sql
│   ├── products.sql
│   ├── production_orders.sql
│   ├── production_yields.sql
│   └── ...
│
│   └── gold/
│       ├── gold_daily_production.sql  # Modelos analíticos que generan tablas para reportería
│       ├── gold_machine_downtime.sql
│       ├── gold_plant_performance.sql
│       └── ...
│
├── src/                               # Código fuente organizado según las etapas del pipeline ETL
│   ├── config/
│   │   └── settings.py                # Gestión de variables de entorno y configuración del proyecto
│   │
│   ├── database/
│   │   └── connection.py              # Crea y administra la conexión hacia PostgreSQL
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── postgres_extractor.py      # Extrae datos desde PostgreSQL y los almacena en Bronze
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── data_cleaning_functions.py # Reglas reutilizables de limpieza y estandarización de datos
│   │   └── transformer.py             # Orquesta la transformación de Bronze hacia Silver
│   │
│   ├── load/
│   │   ├── bigquery_loader.py         # Carga archivos Parquet desde Silver hacia BigQuery
│   │   └── gold_loader.py             # Ejecuta los modelos SQL que construyen la capa Gold
│   │
│   └── validations/                   # Validaciones de calidad de datos y esquemas (Próximamente)
│
├── tests/                             # Pruebas unitarias e integración con pytest (Próximamente)
│   ├── test_transformer.py
│   ├── test_data_cleaning.py
│   └── ...
│
├── utils/
│   └── gcs_uploader.py                # Funciones auxiliares para interactuar con Google Cloud Storage
│
├── .env.example                       # Plantilla de variables de entorno requerida para ejecutar el proyecto
├── .gitignore                         # Exclusión de archivos temporales, credenciales y datos locales
├── LICENSE                            # Licencia de distribución del proyecto
├── README.md                          # Documentación principal y guía de uso
├── requirements.txt                   # Dependencias de Python necesarias para el pipeline
└── main.py                            # Punto de entrada que orquesta la ejecución completa del pipeline
```
