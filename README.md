## 📂 Estructura del Proyecto (En desarrollo)

```text
industrial-maintenance-pipeline/
│
├── .github/
│   └── workflows/
│       └── ci.yml                     # Pipeline de Integración Continua (Próximamente)
│
├── backfill/
│   └── trigger_backfilling.py         # Reprocesamiento de datos históricos
│
├── data/                              # Datos temporales para desarrollo local (Ignorado por Git)
│   ├── bronze/                        # Capa Bronze (CSV)
│   └── silver/                        # Capa Silver (Parquet)
│
├── docs/                              # Diagramas y documentación del proyecto
│
├── sql/
│   ├── *.sql                          # Consultas de extracción desde PostgreSQL
│   └── gold/
│       └── *.sql                      # Modelos analíticos de la capa Gold
│
├── src/                               # Código fuente del pipeline
│   ├── config/
│   │   └── settings.py                # Variables de entorno y configuración
│   │
│   ├── database/
│   │   └── connection.py              # Conexión a PostgreSQL
│   │
│   ├── extractors/
│   │   └── postgres_extractor.py      # Extracción de datos hacia Bronze
│   │
│   ├── transform/
│   │   ├── data_cleaning_functions.py # Funciones de transformación y limpieza
│   │   └── transformer.py             # Proceso Bronze → Silver
│   │
│   ├── load/
│   │   ├── bigquery_loader.py         # Carga de Silver hacia BigQuery
│   │   └── gold_loader.py             # Construcción de la capa Gold
│   │
│   └── validations/                   # Validaciones de calidad (Próximamente)
│
├── tests/                             # Pruebas unitarias y de integración (Próximamente)
│
├── utils/
│   └── gcs_uploader.py                # Utilidades para Cloud Storage
│
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Archivos ignorados por Git
├── LICENSE                            # Licencia del proyecto
├── README.md                          # Documentación principal
├── requirements.txt                   # Dependencias del proyecto
└── main.py                            # Orquestador principal del pipeline
```
