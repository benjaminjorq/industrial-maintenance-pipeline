import json
from pathlib import Path
from datetime import datetime

def save_postgres_metadata(table_name: str, csv_path: Path, row_count: int, generated_at: datetime, query_file: str) -> Path:
    """Genera un archivo JSON con la metadata de la extracción PostgreSQL."""
    metadata = {
        "source": "postgresql",
        "table": table_name,
        "file_name": csv_path.name,
        "rows": row_count,
        "file_size_bytes": csv_path.stat().st_size,
        "generated_at": generated_at.isoformat(),
        "query_file": query_file,
    }
    
    metadata_path = csv_path.parent / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)
        
    return metadata_path

def save_sftp_metadata(table_name: str, file_path: Path, generated_at: datetime, remote_filename: str) -> Path:
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