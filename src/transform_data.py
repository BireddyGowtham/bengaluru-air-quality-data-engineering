import argparse
import pandas as pd

from data_quality import (
    find_iqr_outliers,
    check_valid_ranges,
    find_timestamp_gaps,
    calculate_missing_intervals
)


def load_data(file_path):
    return pd.read_csv(file_path)


def transform_timestamps(df):
    df = df.copy()

    df["datetime_utc"] = pd.to_datetime(
        df["datetime_utc"],
        utc=True
    )

    df["datetime_local"] = pd.to_datetime(
        df["datetime_local"]
    )

    df["local_date"] = df["datetime_local"].dt.date
    df["local_year"] = df["datetime_local"].dt.year
    df["local_month"] = df["datetime_local"].dt.month
    df["local_hour"] = df["datetime_local"].dt.hour

    return df


def standardize_columns(df):
    df = df.copy()

    df = df.rename(
        columns={
            "datetimeUtc": "datetime_utc",
            "datetimeLocal": "datetime_local",
            "isMobile": "is_mobile",
            "isMonitor": "is_monitor"
        }
    )

    return df


def fill_location_metadata(df):
    df = df.copy()

    df["country_iso"] = df["country_iso"].fillna("IN")
    df["is_mobile"] = df["is_mobile"].fillna(False)
    df["is_monitor"] = df["is_monitor"].fillna(True)

    return df
def standardize_data_types(df):
    df = df.copy()

    df["location_id"] = df["location_id"].astype("int64")
    df["value"] = df["value"].astype("float64")

    df["country_iso"] = df["country_iso"].astype("string")
    df["is_mobile"] = df["is_mobile"].astype("bool")
    df["is_monitor"] = df["is_monitor"].astype("bool")

    return df
def find_missing_intervals(df, parameter, expected_minutes=15):
    gaps = find_timestamp_gaps(
        df,
        parameter=parameter,
        expected_minutes=expected_minutes
    )

    gaps = calculate_missing_intervals(
        gaps,
        expected_minutes=expected_minutes
    )

    return gaps

def add_quality_flags(df):
    df = df.copy()

    # Statistical outlier flag
    df["is_statistical_outlier"] = False

    outliers = find_iqr_outliers(df)

    if not outliers.empty:
        outlier_index = outliers.index

        df.loc[
            outlier_index,
            "is_statistical_outlier"
        ] = True

    # Physical validity flag
    df["is_physical_invalid"] = False

    invalid_records = check_valid_ranges(df)

    if not invalid_records.empty:
        invalid_index = invalid_records.index

        df.loc[
            invalid_index,
            "is_physical_invalid"
        ] = True

    # Overall quality flag
    df["quality_flag"] = "normal"

    df.loc[
        df["is_statistical_outlier"],
        "quality_flag"
    ] = "statistical_outlier"

    df.loc[
        df["is_physical_invalid"],
        "quality_flag"
    ] = "physical_range_invalid"

    return df

def parse_arguments():
    """
    Parse command-line arguments for the transformation script.
    """
    parser = argparse.ArgumentParser(
        description="Transform and validate air quality data"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the raw input CSV file"
    )

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_arguments()

    file_path = args.input

    df = load_data(file_path)

    df = transform_timestamps(df)

    

    df = fill_location_metadata(df)

    df = standardize_data_types(df)

    df = add_quality_flags(df)

    print("Missing metadata:")
    print(
        df[
            [
                "country_iso",
                "is_mobile",
                "is_monitor"
            ]
        ].isnull().sum()
    )

    print("\nStatistical outlier flag:")
    print(df["is_statistical_outlier"].value_counts())

    print("\nPhysical validity flag:")
    print(df["is_physical_invalid"].value_counts())

    print("\nQuality flag:")
    print(df["quality_flag"].value_counts())

    print("\nData types:")
    print(df.dtypes)
    print("\nWind speed missing intervals:")

    wind_gaps = find_missing_intervals(
        df,
        parameter="wind_speed",
        expected_minutes=15
    )

    print("Number of gaps:", len(wind_gaps))

    print(
        "Total missing measurements:",
        wind_gaps["missing_intervals"].sum()
    )
    start_date = file_path.split("_")[-2]
    end_date = file_path.split("_")[-1].replace(".csv", "")

    output_path = (
        f"data/processed/"
        f"openaq_measurements_{start_date}_{end_date}.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nTransformed dataset saved to:",
        output_path
    )