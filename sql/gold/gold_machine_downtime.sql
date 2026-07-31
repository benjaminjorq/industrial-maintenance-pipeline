CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_machine_downtime` AS
SELECT
    -- Dividimos por 1.000.000.000 para pasar de nanosegundos a segundos, y luego extraemos la fecha
    DATE(TIMESTAMP_SECONDS(DIV(d.start_timestamp, 1000000000))) AS fecha,
    p.plant_name AS planta,
    m.machine_type AS tipo_maquina,
    d.reason AS motivo_falla,
    -- Hacemos la misma división para calcular la diferencia en minutos
    SUM(TIMESTAMP_DIFF(
        TIMESTAMP_SECONDS(DIV(d.end_timestamp, 1000000000)), 
        TIMESTAMP_SECONDS(DIV(d.start_timestamp, 1000000000)), 
        MINUTE
    )) AS total_minutos_perdidos
FROM `industrial-data-pipeline.industrial_silver.downtime_events` d
JOIN `industrial-data-pipeline.industrial_silver.machines` m 
ON d.machine_id = m.machine_id
JOIN `industrial-data-pipeline.industrial_silver.plants` p 
ON m.plant_id = p.plant_id
WHERE d.end_timestamp > d.start_timestamp
GROUP BY 1, 2, 3, 4;