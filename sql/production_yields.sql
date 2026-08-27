-- Uso de SELECT * justificado por la estructura actual de la fuente, sin impacto relevante en rendimiento.
-- A medida que los datos escalen, se recomienda seleccionar explícitamente las columnas requeridas.

SELECT * 
FROM public.production_yields
