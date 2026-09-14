import pandas as pd
EXPECTED_MEASUREMENTS_PER_DAY = 96

def load_data(file_path):
    return pd.read_csv(file_path)


def pollutant_summary(df):
    summary = (
        df.groupby(["parameter", "unit"])["value"]
        .agg(
            average="mean",
            minimum="min",
            maximum="max",
            standard_deviation="std",
            measurements="count"
        )
        .reset_index()
    )

    return summary


def daily_pollution_trend(df, parameter, unit):
    data = df[
        (df["parameter"] == parameter) &
        (df["unit"] == unit)
    ].copy()

    data["datetime_local"] = pd.to_datetime(data["datetime_local"])
    data["date"] = data["datetime_local"].dt.date

    daily_summary = (
        data.groupby("date")["value"]
        .agg(
            average="mean",
            minimum="min",
            maximum="max",
            measurements="count"
        )
        .reset_index()
    )

    daily_summary["expected_measurements"] = EXPECTED_MEASUREMENTS_PER_DAY

    daily_summary["missing_measurements"] = (
        daily_summary["expected_measurements"]
        - daily_summary["measurements"]
    )

    daily_summary["completeness_pct"] = (
        daily_summary["measurements"]
        / daily_summary["expected_measurements"]
        * 100
    )

    daily_summary["completeness_category"] = (
        daily_summary["completeness_pct"]
        .apply(classify_completeness)
    )

    return daily_summary


def daily_pollution_summary(df):
    data = df.copy()

    data["datetime_local"] = pd.to_datetime(
        data["datetime_local"]
    )

    data["date"] = data["datetime_local"].dt.date

    daily_summary = (
        data.groupby(
            ["date", "parameter", "unit"]
        )["value"]
        .agg(
            average="mean",
            minimum="min",
            maximum="max",
            measurements="count"
        )
        .reset_index()
    )

    daily_summary["completeness_pct"] = (
        daily_summary["measurements"]
        / EXPECTED_MEASUREMENTS_PER_DAY
        * 100
    )

    return daily_summary


def hourly_pollution_pattern(
    df,
    parameter,
    unit,
    exclude_statistical_outliers=False
):
    """
    Calculate average pollution levels by hour of day
    for a specific parameter and unit.
    """

    data = df[
        (df["parameter"] == parameter) &
        (df["unit"] == unit)
    ].copy()

    data["datetime_local"] = pd.to_datetime(
        data["datetime_local"]
    )

    data["hour"] = data["datetime_local"].dt.hour

    if exclude_statistical_outliers:
        data = data[
            data["is_statistical_outlier"] == False
        ]

    hourly_summary = (
        data.groupby("hour")["value"]
        .agg(
            average="mean",
            minimum="min",
            maximum="max",
            measurements="count"
        )
        .reset_index()
    )

    return hourly_summary

def create_weather_pollution_dataset(df):
    data = df.copy()

    data["datetime_local"] = pd.to_datetime(
        data["datetime_local"]
    )

    selected_parameters = [
        "pm25",
        "pm10",
        "no2",
        "o3",
        "temperature",
        "relativehumidity",
        "wind_speed"
    ]

    data = data[
        data["parameter"].isin(selected_parameters)
    ].copy()

    aligned_data = (
        data.pivot_table(
            index="datetime_local",
            columns="parameter",
            values="value",
            aggfunc="mean"
        )
        .reset_index()
    )

    return aligned_data

def calculate_alignment_counts(df):
    data = create_weather_pollution_dataset(df)

    parameters = [
        "pm25",
        "pm10",
        "no2",
        "o3",
        "temperature",
        "relativehumidity",
        "wind_speed"
    ]

    alignment_counts = []

    for parameter in parameters:
        if parameter in data.columns:
            count = data[
                ["pm25", parameter]
            ].dropna().shape[0]

            alignment_counts.append(
                {
                    "pollutant": "pm25",
                    "weather_parameter": parameter,
                    "aligned_measurements": count
                }
            )

    return pd.DataFrame(alignment_counts)

def calculate_weather_correlations(df):

    data = create_weather_pollution_dataset(df)

    weather_parameters = [
        "temperature",
        "relativehumidity",
        "wind_speed"
    ]

    correlations = []

    for parameter in weather_parameters:

        aligned_data = data[
            ["pm25", parameter]
        ].dropna()

        correlation = aligned_data["pm25"].corr(
            aligned_data[parameter]
        )

        correlations.append(
            {
                "pollutant": "pm25",
                "weather_parameter": parameter,
                "aligned_measurements": len(aligned_data),
                "correlation": correlation
            }
        )

    return pd.DataFrame(correlations)

def hourly_weather_pollution_analysis(df):

    data = create_weather_pollution_dataset(df)

    data["datetime_local"] = pd.to_datetime(
        data["datetime_local"]
    )

    data["hour"] = data["datetime_local"].dt.hour

    data["fully_aligned"] = data[
        [
            "pm25",
            "temperature",
            "relativehumidity",
            "wind_speed"
        ]
    ].notna().all(axis=1)

    hourly_summary = (
        data.groupby("hour")
        .agg(
            pm25=("pm25", "mean"),
            temperature=("temperature", "mean"),
            relativehumidity=("relativehumidity", "mean"),
            wind_speed=("wind_speed", "mean"),
            observations=("pm25", "count"),
            fully_aligned_observations=("fully_aligned", "sum")
        )
        .reset_index()
    )

    return hourly_summary

def hourly_aligned_weather_pollution_analysis(df):

    data = create_weather_pollution_dataset(df)

    data["datetime_local"] = pd.to_datetime(
        data["datetime_local"]
    )

    data["hour"] = data["datetime_local"].dt.hour

    data = data[
        [
            "datetime_local",
            "pm25",
            "temperature",
            "relativehumidity",
            "wind_speed",
            "hour"
        ]
    ].dropna()

    hourly_summary = (
        data.groupby("hour")
        .agg(
            pm25=("pm25", "mean"),
            temperature=("temperature", "mean"),
            relativehumidity=("relativehumidity", "mean"),
            wind_speed=("wind_speed", "mean"),
            observations=("pm25", "count")
        )
        .reset_index()
    )

    return hourly_summary

def hourly_weather_completeness(df):
    data = create_weather_pollution_dataset(df)

    data["datetime_local"] = pd.to_datetime(data["datetime_local"])
    data["date"] = data["datetime_local"].dt.date
    data["hour"] = data["datetime_local"].dt.hour

    weather_parameters = [
        "temperature",
        "relativehumidity",
        "wind_speed"
    ]

    # Actual dates on which weather data exists
    weather_dates = data.loc[
        data[weather_parameters].notna().any(axis=1),
        "date"
    ].unique()

    expected_observations = len(weather_dates) * 4

    results = []

    for hour in range(24):
        hour_data = data[data["hour"] == hour]

        for parameter in weather_parameters:

            observed = hour_data[parameter].notna().sum()

            completeness_pct = (
                observed / expected_observations * 100
                if expected_observations > 0
                else 0
            )

            results.append({
                "hour": hour,
                "weather_parameter": parameter,
                "observed_measurements": observed,
                "expected_measurements": expected_observations,
                "completeness_pct": completeness_pct
            })

    return pd.DataFrame(results)

def inspect_weather_dates(df):
    data = create_weather_pollution_dataset(df)

    data["datetime_local"] = pd.to_datetime(data["datetime_local"])
    data["date"] = data["datetime_local"].dt.date

    weather_parameters = [
        "temperature",
        "relativehumidity",
        "wind_speed"
    ]

    daily_weather = (
        data.groupby("date")[weather_parameters]
        .count()
        .reset_index()
    )

    # Keep only dates where at least one weather measurement exists
    daily_weather = daily_weather[
        daily_weather[weather_parameters].sum(axis=1) > 0
    ].copy()

    # Expected observations for a 15-minute interval
    daily_weather["expected_measurements"] = 96

    daily_weather["completeness_pct"] = (
        daily_weather[weather_parameters].mean(axis=1)
        / 96 * 100
    )

    return daily_weather

def classify_completeness(completeness):
    if completeness >= 90:
        return "high"
    elif completeness >= 75:
        return "moderate"
    else:
        return "low"

if __name__ == "__main__":

    file_path = "data/processed/openaq_measurements_transformed.csv"

    df = load_data(file_path)

    summary = pollutant_summary(df)

    print("\nPollutant Summary:")
    print(summary.to_string(index=False))

    pm25_daily = daily_pollution_trend(
        df,
        parameter="pm25",
        unit="µg/m³"
    )

    print("\nPM2.5 Daily Trend:")
    print(
        pm25_daily.head(10).to_string(index=False)
    )

    all_daily = daily_pollution_summary(df)

    print("\nDaily Pollution Summary:")
    print(
        all_daily.head(20).to_string(index=False)
    )
    pm25_hourly = hourly_pollution_pattern(
        df,
        parameter="pm25",
        unit="µg/m³"
    )

    print("\nPM2.5 Hourly Pattern:")
    print(
        pm25_hourly.to_string(index=False)
    )
    pm25_hourly_clean = hourly_pollution_pattern(
        df,
        parameter="pm25",
        unit="µg/m³",
        exclude_statistical_outliers=True
    )

    print("\nPM2.5 Hourly Pattern - Statistical Outliers Excluded:")
    print(
        pm25_hourly_clean.to_string(index=False)
    )
    weather_pollution = create_weather_pollution_dataset(df)

    print("\nWeather + Pollution Dataset:")
    print(
        weather_pollution.head(10).to_string(index=False)
    )
    alignment_counts = calculate_alignment_counts(df)

    print("\nPM2.5 Alignment Counts:")
    print(
        alignment_counts.to_string(index=False)
    )
    weather_correlations = calculate_weather_correlations(df)

    print("\nPM2.5 vs Weather Correlations:")
    print(
        weather_correlations.to_string(index=False)
    )
    hourly_weather = hourly_weather_pollution_analysis(df)

    print("\nHourly Weather + PM2.5 Analysis:")
    print(
        hourly_weather.to_string(index=False)
    )
    aligned_hourly = (
        hourly_aligned_weather_pollution_analysis(df)
    )

    print("\nHourly Fully Aligned Weather + PM2.5 Analysis:")
    print(
        aligned_hourly.to_string(index=False)
    )
    weather_data = create_weather_pollution_dataset(df)

    weather_data["datetime_local"] = pd.to_datetime(
        weather_data["datetime_local"]
    )

    print(
        "\nWeather data date range:",
        weather_data["datetime_local"].min(),
        "to",
        weather_data["datetime_local"].max()
    )

    print(
        "Weather data days:",
        weather_data["datetime_local"].dt.date.nunique()
    )
    completeness = hourly_weather_completeness(df)

    print("\nHourly Weather Completeness:")
    print(
        completeness.to_string(index=False)
    )
    weather_dates = inspect_weather_dates(df)

    print("\nWeather Observations by Date:")
    print(
        weather_dates.to_string(index=False)
    )
    pm25_daily = daily_pollution_trend(
        df,
        parameter="pm25",
        unit="µg/m³"
    )

    print("\nDaily PM2.5 Trend:")
    print(pm25_daily.to_string(index=False))

    pm10_daily = daily_pollution_trend(
        df,
        parameter="pm10",
        unit="µg/m³"
    )

    no2_daily = daily_pollution_trend(
        df,
        parameter="no2",
        unit="µg/m³"
    )

    print("\nDaily PM10 Trend:")
    print(pm10_daily.to_string(index=False))

    print("\nDaily NO2 Trend:")
    print(no2_daily.to_string(index=False))