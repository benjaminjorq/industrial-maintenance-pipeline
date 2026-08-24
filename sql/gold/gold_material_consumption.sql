-- query test 3

CREATE OR REPLACE TABLE `industrial-data-pipeline.maintenance_data.gold_material_consumption` AS
SELECT
    DATE(y.execution_date) AS fecha,
    pr.product_name AS producto_fabricado,
    rm.material_name AS insumo_consumido,
    s.supplier_name AS proveedor,
    -- KPI 1: Total del insumo que se gastó en el piso de fábrica
    SUM((y.good_quantity + y.scrap_quantity) * b.required_quantity) AS consumo_total_estimado
FROM `industrial-data-pipeline.industrial_silver.production_yields` y
JOIN `industrial-data-pipeline.industrial_silver.products` pr 
ON y.product_id = pr.product_id
JOIN `industrial-data-pipeline.industrial_silver.bill_of_materials` b 
ON pr.product_id = b.product_id
JOIN `industrial-data-pipeline.industrial_silver.raw_materials` rm 
ON b.material_id = rm.material_id
JOIN `industrial-data-pipeline.industrial_silver.suppliers` s 
ON rm.supplier_id = s.supplier_id
GROUP BY 1, 2, 3, 4;