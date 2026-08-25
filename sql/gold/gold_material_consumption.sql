-- Shows daily material consumption by product and supplier.
-- Consumption is calculated by multiplying the total production volume
-- by the material quantity required according to the bill of materials (BOM).

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_material_consumption` AS

SELECT
    DATE(y.execution_date) AS date,
    pr.product_name AS product,
    rm.material_name AS material,
    s.supplier_name AS supplier,
    ROUND(SUM((y.good_quantity + y.scrap_quantity) * b.required_quantity), 2) AS quantity_consumed,
    rm.unit_of_measure AS unit

FROM `industrial-data-pipeline.industrial_silver.production_yields` AS y

JOIN `industrial-data-pipeline.industrial_silver.products` AS pr
    ON y.product_id = pr.product_id

JOIN `industrial-data-pipeline.industrial_silver.bill_of_materials` AS b
    ON pr.product_id = b.product_id

JOIN `industrial-data-pipeline.industrial_silver.raw_materials` AS rm
    ON b.material_id = rm.material_id

JOIN `industrial-data-pipeline.industrial_silver.suppliers` AS s
    ON rm.supplier_id = s.supplier_id

GROUP BY
    date,
    product,
    material,
    supplier,
    unit;