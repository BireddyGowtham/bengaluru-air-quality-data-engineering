import pandas as pd


def find_iqr_outliers(df):
    """
    Identify statistical outliers using the IQR method.

    Returns a DataFrame containing:
    parameter, value, unit, datetimeUtc, and datetimeLocal.
    """

    outliers = []

    for parameter in df["parameter"].unique():

        parameter_data = df[
            df["parameter"] == parameter
        ].copy()

        q1 = parameter_data["value"].quantile(0.25)
        q3 = parameter_data["value"].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        parameter_outliers = parameter_data[
            (parameter_data["value"] < lower_bound) |
            (parameter_data["value"] > upper_bound)
        ].copy()

        if not parameter_outliers.empty:
            outliers.append(parameter_outliers)

    if outliers:
        return pd.concat(outliers, ignore_index=True)

    return pd.DataFrame()
def find_logical_duplicates(df):
    """
    Find multiple measurements recorded for the same
    location, parameter, and timestamp.
    """

    duplicates = df[
        df.duplicated(
            subset=[
                "location_id",
                "parameter",
                "datetimeUtc"
            ],
            keep=False
        )
    ].copy()

    return duplicates

def find_timestamp_gaps(df, parameter, expected_minutes=15):
    """
    Find gaps where the time difference between consecutive
    measurements is greater than the expected interval.
    """

    data = df[
        df["parameter"] == parameter
    ].copy()

    # Support both raw and transformed column names
    if "datetime_utc" in data.columns:
        timestamp_column = "datetime_utc"
    elif "datetimeUtc" in data.columns:
        timestamp_column = "datetimeUtc"
    else:
        raise ValueError(
            "DataFrame must contain datetime_utc or datetimeUtc"
        )

    data[timestamp_column] = pd.to_datetime(
        data[timestamp_column],
        utc=True
    )

    data = data.sort_values(timestamp_column)

    data["time_difference"] = (
        data[timestamp_column].diff()
    )

    expected_interval = pd.Timedelta(
        minutes=expected_minutes
    )

    gaps = data[
        data["time_difference"] > expected_interval
    ].copy()

    return gaps
def calculate_missing_intervals(
    gaps,
    expected_minutes=15
):
    """
    Calculate the number of missing measurements
    represented by each timestamp gap.
    """

    expected_interval = pd.Timedelta(
        minutes=expected_minutes
    )

    gaps = gaps.copy()

    gaps["missing_intervals"] = (
        gaps["time_difference"] /
        expected_interval
    ).astype(int) - 1

    return gaps
def check_valid_ranges(df):
    """
    Identify measurements that fall outside basic
    physical/domain sanity ranges.

    Returns a DataFrame containing the invalid records.
    """

    invalid_records = []

    # Relative humidity: 0–100%
    humidity_invalid = df[
        (df["parameter"] == "relativehumidity") &
        (
            (df["value"] < 0) |
            (df["value"] > 100)
        )
    ]

    invalid_records.append(humidity_invalid)

    # Wind direction: 0–360 degrees
    wind_direction_invalid = df[
        (df["parameter"] == "wind_direction") &
        (
            (df["value"] < 0) |
            (df["value"] > 360)
        )
    ]

    invalid_records.append(wind_direction_invalid)

    # Wind speed cannot be negative
    wind_speed_invalid = df[
        (df["parameter"] == "wind_speed") &
        (df["value"] < 0)
    ]

    invalid_records.append(wind_speed_invalid)

    # Temperature: broad sanity range
    temperature_invalid = df[
        (df["parameter"] == "temperature") &
        (
            (df["value"] < -50) |
            (df["value"] > 60)
        )
    ]

    invalid_records.append(temperature_invalid)

    if invalid_records:
        return pd.concat(
        invalid_records
    )

    return pd.DataFrame()
def load_data(file_path):
    """
    Load the raw air-quality dataset.
    """

    return pd.read_csv(file_path)


def print_section(title):
    """
    Print a formatted section heading.
    """

    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

if __name__ == "__main__":

    file_path = "data/raw/openaq_measurements.csv"

    df = load_data(file_path)

    # --------------------------------------------------
    # IQR OUTLIERS
    # --------------------------------------------------

    print_section("IQR OUTLIER SUMMARY")

    outliers = find_iqr_outliers(df)

    summary = (
        outliers
        .groupby(["parameter", "unit"])
        .size()
        .reset_index(name="outlier_count")
        .sort_values("outlier_count", ascending=False)
    )

    print(summary.to_string(index=False))

    print("\nTotal outliers:", len(outliers))

    # --------------------------------------------------
    # LOGICAL DUPLICATES
    # --------------------------------------------------

    print_section("LOGICAL DUPLICATES")

    duplicates = find_logical_duplicates(df)

    print("Duplicate rows:", len(duplicates))

    # --------------------------------------------------
    # TIMESTAMP GAPS
    # --------------------------------------------------

    print_section("WIND SPEED TIMESTAMP GAPS")

    wind_gaps = find_timestamp_gaps(
        df,
        parameter="wind_speed",
        expected_minutes=15
    )

    print("Number of gaps:", len(wind_gaps))

    wind_gaps = calculate_missing_intervals(
        wind_gaps
    )

    print(
        "Total missing measurements:",
        wind_gaps["missing_intervals"].sum()
    )

    # --------------------------------------------------
    # PARAMETER DATE RANGES
    # --------------------------------------------------

    print_section("PARAMETER DATE RANGES")

    parameter_dates = (
        df.groupby("parameter")["datetimeUtc"]
        .agg(["min", "max"])
        .reset_index()
    )

    print(parameter_dates.to_string(index=False))

    # --------------------------------------------------
    # PHYSICAL RANGE VALIDATION
    # --------------------------------------------------

    print_section("PHYSICAL RANGE VALIDATION")

    invalid_records = check_valid_ranges(df)

    print(
        "Invalid records:",
        len(invalid_records)
    )