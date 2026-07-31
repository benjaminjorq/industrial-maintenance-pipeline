import logging
from pathlib import Path
from google.cloud import storage

logger = logging.getLogger(__name__)

def upload_file(local_file_path: Path, bucket_name: str, cloud_destination_path: str) -> bool:
    """Carga un archivo local hacia una ubicación específica en Cloud Storage.

    Args:
        local_file_path: Ruta local del archivo que será cargado.
        bucket_name: Nombre del bucket destino en Cloud Storage.
        cloud_destination_path: Ruta del objeto dentro del bucket.

    Returns:
        True si la carga fue exitosa, False si ocurrió un error durante el proceso.
    """
    try:
        logger.info("Preparando envío a la nube: %s", local_file_path.name)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(cloud_destination_path)
        
        logger.info("Subiendo hacia el bucket '%s' en la ruta: %s", bucket_name, cloud_destination_path)
        blob.upload_from_filename(str(local_file_path))
        
        logger.info("Archivo subido exitosamente a Cloud Storage.")
        return True
        
    except Exception as error:
        logger.error("Error crítico al intentar subir el archivo a GCP: %s", str(error), exc_info=True)
        return False