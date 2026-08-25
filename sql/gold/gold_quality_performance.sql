-- Shows quality control performance by plant.
-- The approval percentage represents the proportion of approved inspections
-- relative to the total number of inspections performed at each plant.

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_quality_performance` AS

SELECT
    p.plant_name AS plant,
    COUNT(q.quality_id) AS inspections_performed,
    ROUND(AVG(q.quality_score), 2) AS average_quality_score,
    COUNTIF(q.is_approved) AS approved_inspections,
    ROUND(SAFE_DIVIDE(COUNTIF(q.is_approved), COUNT(q.quality_id)) * 100, 2) AS approval_percentage

FROM `industrial-data-pipeline.industrial_silver.quality_control` AS q

JOIN `industrial-data-pipeline.industrial_silver.production_yields` AS y
    ON q.production_yield_id = y.yield_id

JOIN `industrial-data-pipeline.industrial_silver.machines` AS m
    ON y.machine_id = m.machine_id

JOIN `industrial-data-pipeline.industrial_silver.plants` AS p
    ON m.plant_id = p.plant_id

GROUP BY
    plant;