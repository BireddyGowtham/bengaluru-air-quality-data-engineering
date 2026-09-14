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