-- Shows historical production performance by plant and region.
-- The quality percentage represents the proportion of good units
-- relative to total production, including good and rejected units.

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_plant_performance` AS

SELECT
    p.plant_name AS plant,
    p.region AS region,
    SUM(y.good_quantity) AS good_units,
    SUM(y.scrap_quantity) AS rejected_units,
    ROUND(SAFE_DIVIDE(SUM(y.good_quantity), SUM(y.good_quantity + y.scrap_quantity)) * 100, 2) AS quality_percentage

FROM `industrial-data-pipeline.industrial_silver.production_yields` AS y

JOIN `industrial-data-pipeline.industrial_silver.machines` AS m
    ON y.machine_id = m.machine_id

JOIN `industrial-data-pipeline.industrial_silver.plants` AS p
    ON m.plant_id = p.plant_id

GROUP BY
    plant,
    region;