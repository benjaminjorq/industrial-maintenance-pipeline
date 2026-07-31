CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_daily_production` AS
SELECT
    DATE(y.execution_date) AS fecha,
    p.plant_name AS planta,
    pr.product_name AS producto,
    -- KPI 1: Total fabricado (bueno + malo)
    SUM(y.good_quantity + y.scrap_quantity) AS produccion_total,
    -- KPI 2: Costo de lo que salió bien (Protegido contra NULLs)
    SUM(y.good_quantity * COALESCE(pr.standard_cost, 0)) AS costo_produccion_buena
FROM `industrial-data-pipeline.industrial_silver.production_yields` y
JOIN `industrial-data-pipeline.industrial_silver.machines` m 
ON y.machine_id = m.machine_id
JOIN `industrial-data-pipeline.industrial_silver.plants` p 
ON m.plant_id = p.plant_id
JOIN `industrial-data-pipeline.industrial_silver.products` pr 
ON y.product_id = pr.product_id
GROUP BY 1, 2, 3;