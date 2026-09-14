-- 04_pollution_analysis.sql

-- 1. Daily PM2.5 Pollution Trend

SELECT
    measurement_date,
    average_pm25,
    minimum_pm25,
    maximum_pm25,
    measurements,
    completeness_pct
FROM vw_daily_pm25
ORDER BY measurement_date;


-- 2. Top 10 PM2.5 Pollution Days
-- Only include days with at least 90% data completeness

SELECT
    measurement_date,
    average_pm25,
    minimum_pm25,
    maximum_pm25,
    measurements,
    completeness_pct
FROM vw_daily_pm25
WHERE completeness_pct >= 90
ORDER BY average_pm25 DESC
FETCH FIRST 10 ROWS ONLY;

-- 3. Hourly PM2.5 Pattern

SELECT
    hour_of_day,
    average_pm25,
    minimum_pm25,
    maximum_pm25,
    measurements
FROM vw_hourly_pm25
ORDER BY hour_of_day;

-- 4. PM2.5 by Time of Day

SELECT
    CASE
        WHEN hour_of_day BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour_of_day BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN hour_of_day BETWEEN 17 AND 21 THEN 'Evening'
        ELSE 'Night'
    END AS time_period,

    ROUND(AVG(average_pm25), 2) AS avg_pm25

FROM vw_hourly_pm25

GROUP BY
    CASE
        WHEN hour_of_day BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour_of_day BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN hour_of_day BETWEEN 17 AND 21 THEN 'Evening'
        ELSE 'Night'
    END

ORDER BY avg_pm25 DESC;

-- 5. Daily PM10 Pollution Trend

SELECT
    TRUNC(CAST(datetime_local AS DATE)) AS measurement_date,

    ROUND(AVG(value), 2) AS average_pm10,

    MIN(value) AS minimum_pm10,

    MAX(value) AS maximum_pm10,

    COUNT(*) AS measurements

FROM air_quality_measurements

WHERE parameter = 'pm10'
  AND unit = 'µg/m³'

GROUP BY TRUNC(CAST(datetime_local AS DATE))

ORDER BY measurement_date;

-- 6. Top 10 PM10 Pollution Days

SELECT
    TRUNC(CAST(datetime_local AS DATE)) AS measurement_date,

    ROUND(AVG(value), 2) AS average_pm10,

    MIN(value) AS minimum_pm10,

    MAX(value) AS maximum_pm10,

    COUNT(*) AS measurements

FROM air_quality_measurements

WHERE parameter = 'pm10'
  AND unit = 'µg/m³'

GROUP BY TRUNC(CAST(datetime_local AS DATE))

ORDER BY average_pm10 DESC

FETCH FIRST 10 ROWS ONLY;

-- 7. Top 10 Reliable PM10 Pollution Days
-- Only include days with at least 90% completeness

SELECT
    measurement_date,
    average_pm10,
    minimum_pm10,
    maximum_pm10,
    measurements,
    ROUND(measurements / 96 * 100, 2) AS completeness_pct

FROM (
    SELECT
        TRUNC(CAST(datetime_local AS DATE)) AS measurement_date,

        ROUND(AVG(value), 2) AS average_pm10,

        MIN(value) AS minimum_pm10,

        MAX(value) AS maximum_pm10,

        COUNT(*) AS measurements

    FROM air_quality_measurements

    WHERE parameter = 'pm10'
      AND unit = 'µg/m³'

    GROUP BY TRUNC(CAST(datetime_local AS DATE))
)

WHERE measurements >= 86.4

ORDER BY average_pm10 DESC

FETCH FIRST 10 ROWS ONLY;

-- 8. Daily NO2 Pollution Trend

SELECT
    TRUNC(CAST(datetime_local AS DATE)) AS measurement_date,

    ROUND(AVG(value), 2) AS average_no2,

    MIN(value) AS minimum_no2,

    MAX(value) AS maximum_no2,

    COUNT(*) AS measurements

FROM air_quality_measurements

WHERE parameter = 'no2'
  AND unit = 'µg/m³'

GROUP BY TRUNC(CAST(datetime_local AS DATE))

ORDER BY measurement_date;

-- 9. Top 10 Reliable NO2 Pollution Days
-- Only include days with at least 90% completeness

SELECT
    measurement_date,
    average_no2,
    minimum_no2,
    maximum_no2,
    measurements,
    ROUND(measurements / 96 * 100, 2) AS completeness_pct

FROM (
    SELECT
        TRUNC(CAST(datetime_local AS DATE)) AS measurement_date,

        ROUND(AVG(value), 2) AS average_no2,

        MIN(value) AS minimum_no2,

        MAX(value) AS maximum_no2,

        COUNT(*) AS measurements

    FROM air_quality_measurements

    WHERE parameter = 'no2'
      AND unit = 'µg/m³'

    GROUP BY TRUNC(CAST(datetime_local AS DATE))
)

WHERE measurements >= 87

ORDER BY average_no2 DESC

FETCH FIRST 10 ROWS ONLY;

-- 10. Overall Pollutant Summary

SELECT
    parameter,
    unit,
    COUNT(*) AS total_measurements,
    ROUND(AVG(value), 2) AS average_value,
    MIN(value) AS minimum_value,
    MAX(value) AS maximum_value,

    SUM(
        CASE
            WHEN is_statistical_outlier = 1 THEN 1
            ELSE 0
        END
    ) AS statistical_outliers

FROM air_quality_measurements

WHERE parameter IN ('pm25', 'pm10', 'no2')

GROUP BY
    parameter,
    unit

ORDER BY parameter, unit;

-- 11. PM2.5 vs PM10 Correlation

SELECT
    ROUND(
        CORR(pm25_value, pm10_value),
        4
    ) AS pm25_pm10_correlation

FROM (
    SELECT
        pm25.datetime_local,
        pm25.value AS pm25_value,
        pm10.value AS pm10_value

    FROM air_quality_measurements pm25

    JOIN air_quality_measurements pm10
        ON pm25.datetime_local = pm10.datetime_local

    WHERE pm25.parameter = 'pm25'
      AND pm25.unit = 'µg/m³'

      AND pm10.parameter = 'pm10'
      AND pm10.unit = 'µg/m³'
);