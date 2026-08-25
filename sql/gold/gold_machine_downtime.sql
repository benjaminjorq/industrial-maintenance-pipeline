-- Shows downtime by plant, machine type, and failure reason.
-- Lost minutes represent the total duration of downtime events.

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_machine_downtime` AS

SELECT
    DATE(d.start_timestamp) AS date,
    p.plant_name AS plant,
    m.machine_type AS machine_type,
    d.reason AS failure_reason,
    SUM(TIMESTAMP_DIFF(d.end_timestamp, d.start_timestamp, MINUTE)) AS downtime_minutes

FROM `industrial-data-pipeline.industrial_silver.downtime_events` AS d

JOIN `industrial-data-pipeline.industrial_silver.machines` AS m
    ON d.machine_id = m.machine_id

JOIN `industrial-data-pipeline.industrial_silver.plants` AS p
    ON m.plant_id = p.plant_id

WHERE d.end_timestamp > d.start_timestamp

GROUP BY
    date,
    plant,
    machine_type,
    failure_reason;