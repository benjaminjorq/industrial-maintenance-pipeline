# Imagen base oficial de Python optimizada
FROM python:3.12-slim

# Configuración de Python para mejorar logs y evitar archivos innecesarios
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema requeridas por PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar dependencias primero para aprovechar caché de Docker
COPY requirements.txt .

# Instalar librerías del pipeline
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del proyecto
COPY . .

# Ejecutar pipeline al iniciar el contenedor
CMD ["python", "main.py"]