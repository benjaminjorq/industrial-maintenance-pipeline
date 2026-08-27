import logging
from pathlib import Path
import posixpath
import paramiko
import json
from datetime import datetime, timezone

from src.config.settings import (
    SFTP_HOST, SFTP_PORT, SFTP_USER, 
    SFTP_PASSWORD, SFTP_REMOTE_PATH
)
from utils.gcs_uploader import upload_file
from src.config.settings import GCS_BUCKET_BRONZE

logger = logging.getLogger(__name__)

def save_metadata(table_name: str, file_path: Path, generated_at: datetime, remote_filename: str) -> Path:
    """Genera un archivo JSON con la metadata de la extracción SFTP."""
    metadata = {
        "source": "sftp",
        "table": table_name,
        "file_name": file_path.name,
        "file_size_bytes": file_path.stat().st_size,
        "generated_at": generated_at.isoformat(),
        "remote_source_file": remote_filename
    }
    
    metadata_path = file_path.parent / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)
        
    return metadata_path

def run(table_name: str, bronze_path: Path, ingestion_date: str, remote_filename: str) -> None:
    logger.info("Iniciando extracción SFTP para la tabla externa: '%s'", table_name)
    
    output_dir = bronze_path / table_name / f"ingestion_date={ingestion_date}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    local_filename = f"{table_name}_{ingestion_date}.csv"
    local_filepath = output_dir / local_filename
    
    cloud_folder = f"{table_name}/ingestion_date={ingestion_date}"

    ssh_client = paramiko.SSHClient()
    
    # Verifica la identidad del servidor mediante una host key previamente confiada.
    # Las claves desconocidas o modificadas son rechazadas automáticamente.
    
    ssh_client.load_system_host_keys('known_hosts')
    ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())

    sftp = None

    try:
        logger.info("Conectando al servidor SFTP: %s", SFTP_HOST)
        ssh_client.connect(
            hostname=SFTP_HOST,
            port=int(SFTP_PORT),
            username=SFTP_USER,
            password=SFTP_PASSWORD,
            timeout=15
        )
        
        sftp = ssh_client.open_sftp()
        
        remote_filepath = posixpath.join(SFTP_REMOTE_PATH, remote_filename)
        logger.info("Descargando archivo remoto: %s", remote_filepath)
        
        sftp.get(remote_filepath, str(local_filepath))
        logger.info("Archivo descargado exitosamente en: %s", local_filepath)

        now = datetime.now(timezone.utc)
        metadata_path = save_metadata(table_name, local_filepath, now, remote_filename)
        
        logger.info("Respaldando archivo SFTP y metadatos en Cloud Storage (Bronze)")

        upload_csv_ok = upload_file(local_filepath, GCS_BUCKET_BRONZE, f"{cloud_folder}/{local_filename}")
        upload_meta_ok = upload_file(metadata_path, GCS_BUCKET_BRONZE, f"{cloud_folder}/{metadata_path.name}")
        
        if not upload_csv_ok or not upload_meta_ok:
             raise RuntimeError("Fallo crítico: GCS Uploader retornó False. No se pudo respaldar en la nube.")
        
    except Exception as error:
        logger.error("Error crítico durante la extracción SFTP de '%s': %s", table_name, error, exc_info=True)
        raise
        
    finally:
        if sftp is not None:
            sftp.close()
        ssh_client.close()
        logger.info("Conexión SFTP cerrada.")