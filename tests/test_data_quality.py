import pandas as pd

from src.data_quality import find_logical_duplicates


def test_find_logical_duplicates():

    df = pd.DataFrame({
        "location_id": [6973, 6973, 6973],
        "parameter": ["pm25", "pm25", "pm10"],
        "datetimeUtc": [
            "2025-02-19T02:15:00Z",
            "2025-02-19T02:15:00Z",
            "2025-02-19T02:15:00Z"
        ],
        "value": [70, 72, 126],
        "unit": ["µg/m³", "µg/m³", "µg/m³"]
    })

    duplicates = find_logical_duplicates(df)

    assert len(duplicates) == 2

from src.data_quality import find_iqr_outliers


def test_find_iqr_outliers():

    df = pd.DataFrame({
        "parameter": [
            "pm25",
            "pm25",
            "pm25",
            "pm25",
            "pm25"
        ],
        "value": [
            10,
            11,
            12,
            13,
            100
        ],
        "unit": [
            "µg/m³",
            "µg/m³",
            "µg/m³",
            "µg/m³",
            "µg/m³"
        ],
        "datetimeUtc": [
            "2025-01-01T00:00:00Z",
            "2025-01-01T00:15:00Z",
            "2025-01-01T00:30:00Z",
            "2025-01-01T00:45:00Z",
            "2025-01-01T01:00:00Z"
        ],
        "datetimeLocal": [
            "2025-01-01T05:30:00+05:30",
            "2025-01-01T05:45:00+05:30",
            "2025-01-01T06:00:00+05:30",
            "2025-01-01T06:15:00+05:30",
            "2025-01-01T06:30:00+05:30"
        ]
    })

    outliers = find_iqr_outliers(df)

    assert len(outliers) == 1
    assert outliers.iloc[0]["value"] == 100
from src.data_quality import check_valid_ranges


def test_check_valid_ranges():

    df = pd.DataFrame({
        "parameter": [
            "relativehumidity",
            "wind_direction",
            "wind_speed",
            "temperature"
        ],
        "value": [
            150,
            400,
            -5,
            100
        ],
        "unit": [
            "%",
            "deg",
            "m/s",
            "c"
        ]
    })

    invalid_records = check_valid_ranges(df)

    assert len(invalid_records) == 4

from src.data_quality import (
    find_timestamp_gaps,
    calculate_missing_intervals
)


def test_timestamp_gaps():

    df = pd.DataFrame({
        "parameter": [
            "wind_speed",
            "wind_speed",
            "wind_speed",
            "wind_speed"
        ],
        "datetimeUtc": [
            "2025-01-01T10:00:00Z",
            "2025-01-01T10:15:00Z",
            "2025-01-01T10:30:00Z",
            "2025-01-01T11:00:00Z"
        ]
    })

    gaps = find_timestamp_gaps(
        df,
        parameter="wind_speed",
        expected_minutes=15
    )

    assert len(gaps) == 1

    gaps = calculate_missing_intervals(gaps)

    assert gaps.iloc[0]["missing_intervals"] == 1
def test_no_timestamp_gaps():

    df = pd.DataFrame({
        "parameter": [
            "wind_speed",
            "wind_speed",
            "wind_speed",
            "wind_speed"
        ],
        "datetimeUtc": [
            "2025-01-01T10:00:00Z",
            "2025-01-01T10:15:00Z",
            "2025-01-01T10:30:00Z",
            "2025-01-01T10:45:00Z"
        ]
    })

    gaps = find_timestamp_gaps(
        df,
        parameter="wind_speed",
        expected_minutes=15
    )

    assert len(gaps) == 0