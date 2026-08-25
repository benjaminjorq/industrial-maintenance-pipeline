FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# known_hosts contiene la identidad confiable del servidor SFTP y permite utilizar
# RejectPolicy para rechazar servidores desconocidos o con una host key diferente.
RUN mkdir -p /root/.ssh
COPY known_hosts /root/.ssh/known_hosts
RUN chmod 600 /root/.ssh/known_hosts

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]