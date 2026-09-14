-- 03_quality_analysis.sql

-- 1. Overall Data Quality Summary

SELECT
    quality_flag,
    COUNT(*) AS record_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM air_quality_measurements),
        2
    ) AS percentage
FROM air_quality_measurements
GROUP BY quality_flag
ORDER BY record_count DESC;

-- 2. Outlier Percentage by Parameter

SELECT
    parameter,
    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN is_statistical_outlier = 1 THEN 1
            ELSE 0
        END
    ) AS outlier_records,

    ROUND(
        SUM(
            CASE
                WHEN is_statistical_outlier = 1 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS outlier_percentage

FROM air_quality_measurements

GROUP BY parameter

ORDER BY outlier_percentage DESC;

-- 3. Daily PM2.5 Completeness

SELECT
    measurement_date,
    measurements,
    missing_measurements,
    completeness_pct,
    completeness_category
FROM vw_daily_pm25
ORDER BY measurement_date;

-- 4. Five Worst PM2.5 Monitoring Days

SELECT
    measurement_date,
    measurements,
    missing_measurements,
    completeness_pct,
    completeness_category
FROM vw_daily_pm25
ORDER BY completeness_pct ASC
FETCH FIRST 5 ROWS ONLY;

-- 5. PM2.5 Timestamp Gap Analysis
-- Expected measurement interval = 15 minutes

SELECT
    parameter,
    datetime_local,
    previous_timestamp,
    gap_minutes,
    ROUND(gap_minutes / 15) - 1 AS missing_measurements
FROM (
    SELECT
        parameter,
        datetime_local,

        LAG(datetime_local) OVER (
            PARTITION BY parameter
            ORDER BY datetime_local
        ) AS previous_timestamp,

        ROUND(
            (
                CAST(datetime_local AS DATE)
                -
                CAST(
                    LAG(datetime_local) OVER (
                        PARTITION BY parameter
                        ORDER BY datetime_local
                    ) AS DATE
                )
            ) * 24 * 60,
            2
        ) AS gap_minutes

    FROM air_quality_measurements

    WHERE parameter = 'pm25'
      AND unit = 'µg/m³'
)
WHERE gap_minutes > 15
  AND gap_minutes <= 1440
ORDER BY gap_minutes DESC;

-- 6. PM2.5 Gap Summary

SELECT
    COUNT(*) AS gap_events,

    SUM(
        ROUND(gap_minutes / 15) - 1
    ) AS total_missing_measurements,

    MAX(gap_minutes) AS largest_gap_minutes,

    ROUND(
        MAX(gap_minutes) / 60,
        2
    ) AS largest_gap_hours

FROM (
    SELECT
        gap_minutes
    FROM (
        SELECT
            ROUND(
                (
                    CAST(datetime_local AS DATE)
                    -
                    CAST(
                        LAG(datetime_local) OVER (
                            PARTITION BY parameter
                            ORDER BY datetime_local
                        ) AS DATE
                    )
                ) * 24 * 60,
                2
            ) AS gap_minutes

        FROM air_quality_measurements

        WHERE parameter = 'pm25'
          AND unit = 'µg/m³'
    )
    WHERE gap_minutes > 15
      AND gap_minutes <= 1440
);

-- 7. Data Quality Summary by Parameter

SELECT
    parameter,

    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN quality_flag = 'normal' THEN 1
            ELSE 0
        END
    ) AS normal_records,

    SUM(
        CASE
            WHEN quality_flag = 'statistical_outlier' THEN 1
            ELSE 0
        END
    ) AS statistical_outliers,

    SUM(
        CASE
            WHEN quality_flag = 'physical_range_invalid' THEN 1
            ELSE 0
        END
    ) AS physical_invalid_records

FROM air_quality_measurements

GROUP BY parameter

ORDER BY parameter;