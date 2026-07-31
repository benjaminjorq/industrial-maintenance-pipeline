import logging
from main import main

logger = logging.getLogger(__name__)

# Parámetros de ejecución para reprocesamiento
# Instrucciones de mantenimiento:
# Modifica 'target_date' con la fecha exacta del día que deseas recuperar.
# En 'failed_tables', coloca únicamente el nombre de las tablas afectadas para no sobrecargar el sistema.
# Si necesitas reprocesar todas las tablas de ese día, asigna: failed_tables = None

target_date = "2026-07-01"
failed_tables = ["production_orders", "quality_control"]

logger.info("Iniciando proceso de recuperación (backfill)")
logger.info("Fecha asignada para reproceso: %s", target_date)
logger.info("Tablas seleccionadas: %s", failed_tables)

try:
    main(target_date=target_date, target_tables=failed_tables)
    logger.info("Proceso de recuperación completado exitosamente.")

except Exception as error:
    logger.error("Error durante la ejecución del proceso de recuperación: %s", str(error), exc_info=True)