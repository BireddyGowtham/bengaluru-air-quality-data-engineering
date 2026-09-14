-- 05_weather_analysis.sql
--
-- Purpose:
-- Analyze the relationship between PM2.5 pollution
-- and weather conditions in Bengaluru.
--
-- Weather variables:
--   - Temperature
--   - Relative Humidity
--   - Wind Speed
--   - Wind Direction


-- =========================================================
-- 1. PM2.5 and Weather Timestamp Alignment
-- =========================================================
--
-- Pivot parameter-level measurements into columns
-- using datetime_local as the common timestamp.
--
-- This query is mainly useful for inspecting how the
-- different measurements align over time.

SELECT
    datetime_local,

    MAX(
        CASE
            WHEN parameter = 'pm25'
                 AND unit = 'µg/m³'
            THEN value
        END
    ) AS pm25,

    MAX(
        CASE
            WHEN parameter = 'temperature'
            THEN value
        END
    ) AS temperature,

    MAX(
        CASE
            WHEN parameter = 'relativehumidity'
            THEN value
        END
    ) AS relative_humidity,

    MAX(
        CASE
            WHEN parameter = 'wind_speed'
            THEN value
        END
    ) AS wind_speed,

    MAX(
        CASE
            WHEN parameter = 'wind_direction'
            THEN value
        END
    ) AS wind_direction

FROM air_quality_measurements

WHERE parameter IN (
    'pm25',
    'temperature',
    'relativehumidity',
    'wind_speed',
    'wind_direction'
)

GROUP BY datetime_local

ORDER BY datetime_local;


-- =========================================================
-- 2. Fully Aligned PM2.5 and Weather Observations
-- =========================================================
--
-- Keep only timestamps where PM2.5 and every required
-- weather measurement are available.

SELECT
    datetime_local,

    MAX(
        CASE
            WHEN parameter = 'pm25'
                 AND unit = 'µg/m³'
            THEN value
        END
    ) AS pm25,

    MAX(
        CASE
            WHEN parameter = 'temperature'
            THEN value
        END
    ) AS temperature,

    MAX(
        CASE
            WHEN parameter = 'relativehumidity'
            THEN value
        END
    ) AS relative_humidity,

    MAX(
        CASE
            WHEN parameter = 'wind_speed'
            THEN value
        END
    ) AS wind_speed,

    MAX(
        CASE
            WHEN parameter = 'wind_direction'
            THEN value
        END
    ) AS wind_direction

FROM air_quality_measurements

WHERE parameter IN (
    'pm25',
    'temperature',
    'relativehumidity',
    'wind_speed',
    'wind_direction'
)

GROUP BY datetime_local

HAVING
    MAX(
        CASE
            WHEN parameter = 'pm25'
                 AND unit = 'µg/m³'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'temperature'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'relativehumidity'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'wind_speed'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'wind_direction'
            THEN value
        END
    ) IS NOT NULL

ORDER BY datetime_local;


-- =========================================================
-- 3. Reusable PM2.5 and Weather Alignment View
-- =========================================================
--
-- Create a reusable dataset containing only timestamps
-- where all required measurements are available.

CREATE OR REPLACE VIEW vw_pm25_weather_aligned AS

SELECT
    datetime_local,

    MAX(
        CASE
            WHEN parameter = 'pm25'
                 AND unit = 'µg/m³'
            THEN value
        END
    ) AS pm25,

    MAX(
        CASE
            WHEN parameter = 'temperature'
            THEN value
        END
    ) AS temperature,

    MAX(
        CASE
            WHEN parameter = 'relativehumidity'
            THEN value
        END
    ) AS relative_humidity,

    MAX(
        CASE
            WHEN parameter = 'wind_speed'
            THEN value
        END
    ) AS wind_speed,

    MAX(
        CASE
            WHEN parameter = 'wind_direction'
            THEN value
        END
    ) AS wind_direction

FROM air_quality_measurements

WHERE parameter IN (
    'pm25',
    'temperature',
    'relativehumidity',
    'wind_speed',
    'wind_direction'
)

GROUP BY datetime_local

HAVING
    MAX(
        CASE
            WHEN parameter = 'pm25'
                 AND unit = 'µg/m³'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'temperature'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'relativehumidity'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'wind_speed'
            THEN value
        END
    ) IS NOT NULL

    AND

    MAX(
        CASE
            WHEN parameter = 'wind_direction'
            THEN value
        END
    ) IS NOT NULL;


-- =========================================================
-- 4. Test the Reusable Alignment View
-- =========================================================

SELECT *
FROM vw_pm25_weather_aligned
FETCH FIRST 10 ROWS ONLY;


-- =========================================================
-- 5. Weather Correlation Summary
-- =========================================================
--
-- Calculate Pearson correlation between PM2.5 and
-- selected weather variables.
--
-- Correlation:
--   +1 = strong positive linear relationship
--    0 = no linear relationship
--   -1 = strong negative linear relationship

SELECT
    ROUND(
        CORR(pm25, temperature),
        6
    ) AS pm25_temperature_correlation,

    ROUND(
        CORR(pm25, relative_humidity),
        6
    ) AS pm25_humidity_correlation,

    ROUND(
        CORR(pm25, wind_speed),
        6
    ) AS pm25_wind_speed_correlation

FROM vw_pm25_weather_aligned;