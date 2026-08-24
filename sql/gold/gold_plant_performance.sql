-- query test 3

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_plant_performance` AS
SELECT
    p.plant_name AS planta,
    p.region AS region,
    -- KPI 1: Piezas buenas históricas
    SUM(y.good_quantity) AS total_piezas_buenas,
    -- KPI 2: Chatarra histórica
    SUM(y.scrap_quantity) AS total_scrap,
    -- KPI 3: Porcentaje de calidad (Protegido contra división por cero)
    ROUND(
        SAFE_DIVIDE(
            SUM(y.good_quantity),
            SUM(y.good_quantity) + SUM(y.scrap_quantity)
        ) * 100, 
    2) AS porcentaje_calidad
FROM `industrial-data-pipeline.industrial_silver.plants` p
JOIN `industrial-data-pipeline.industrial_silver.machines` m 
ON p.plant_id = m.plant_id
JOIN `industrial-data-pipeline.industrial_silver.production_yields` y 
ON m.machine_id = y.machine_id
GROUP BY 1, 2;