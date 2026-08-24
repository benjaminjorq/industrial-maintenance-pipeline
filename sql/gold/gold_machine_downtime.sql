-- Query test 2

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_machine_downtime` AS
SELECT 
    DATE(d.start_timestamp) AS fecha,
    p.plant_name AS planta,
    m.machine_type AS tipo_maquina,
    d.reason AS motivo_falla,
    -- Mira qué limpio queda el cálculo de minutos ahora:
    SUM(TIMESTAMP_DIFF(d.end_timestamp, d.start_timestamp, MINUTE)) AS total_minutos_perdidos
FROM `industrial-data-pipeline.industrial_silver.downtime_events` d
JOIN `industrial-data-pipeline.industrial_silver.machines` m
  ON d.machine_id = m.machine_id
JOIN `industrial-data-pipeline.industrial_silver.plants` p
  ON m.plant_id = p.plant_id
WHERE d.end_timestamp > d.start_timestamp
GROUP BY 1, 2, 3, 4;