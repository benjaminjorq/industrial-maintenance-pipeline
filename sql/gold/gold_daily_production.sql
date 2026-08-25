-- Shows daily production volume and cost by plant and product.

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_daily_production` AS

SELECT
    DATE(y.execution_date) AS date,
    p.plant_name AS plant,
    pr.product_name AS product,
    SUM(y.good_quantity + y.scrap_quantity) AS production_volume,
    ROUND(SUM(y.good_quantity * pr.standard_cost), 2) AS production_cost

FROM `industrial-data-pipeline.industrial_silver.production_yields` AS y

JOIN `industrial-data-pipeline.industrial_silver.machines` AS m
    ON y.machine_id = m.machine_id

JOIN `industrial-data-pipeline.industrial_silver.plants` AS p
    ON m.plant_id = p.plant_id

JOIN `industrial-data-pipeline.industrial_silver.products` AS pr
    ON y.product_id = pr.product_id

GROUP BY
    date,
    plant,
    product;