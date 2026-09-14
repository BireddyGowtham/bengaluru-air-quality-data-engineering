import matplotlib.pyplot as plt
import pandas as pd

from analytics import (
    daily_pollution_trend,
    hourly_pollution_pattern,
    create_weather_pollution_dataset
)


def plot_daily_pollution_trend(data, parameter, output_path):
    """
    Plot daily pollution averages while preserving gaps
    between separate measurement periods.
    """

    data = data.copy()

    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").reset_index(drop=True)

    # Detect gaps between available dates
    data["date_gap"] = data["date"].diff().dt.days

    # Prevent a line from being drawn across large data gaps
    data.loc[data["date_gap"] > 1, "average"] = float("nan")

    plt.figure(figsize=(12, 6))

    plt.plot(
        data["date"],
        data["average"],
        marker="o"
    )

    plt.xlabel("Date")
    plt.ylabel(f"{parameter.upper()} (µg/m³)")
    plt.title(f"Daily {parameter.upper()} Trend")

    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Visualization saved to: {output_path}")

    plt.close()

def plot_hourly_pollution_pattern(data, parameter, output_path):
    """
    Plot average pollution levels by hour of day.
    """

    data = data.copy()

    data = data.sort_values("hour")

    plt.figure(figsize=(12, 6))

    plt.plot(
        data["hour"],
        data["average"],
        marker="o"
    )

    display_name = "PM2.5" if parameter == "pm25" else parameter.upper()

    plt.xlabel("Hour of Day")
    plt.ylabel(f"{display_name} (µg/m³)")
    plt.title(f"Hourly {display_name} Pattern")

    plt.xticks(range(24))
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Visualization saved to: {output_path}")

    plt.close()

def plot_pm25_outlier_comparison(
    original_data,
    cleaned_data,
    output_path
):
    """
    Compare hourly PM2.5 averages before and after
    excluding statistical outliers.
    """

    original_data = original_data.sort_values("hour")
    cleaned_data = cleaned_data.sort_values("hour")

    plt.figure(figsize=(12, 6))

    plt.plot(
        original_data["hour"],
        original_data["average"],
        marker="o",
        label="All observations"
    )

    plt.plot(
        cleaned_data["hour"],
        cleaned_data["average"],
        marker="o",
        label="Statistical outliers excluded"
    )

    plt.xlabel("Hour of Day")
    plt.ylabel("PM2.5 (µg/m³)")
    plt.title("PM2.5 Hourly Pattern: Outlier Comparison")

    plt.xticks(range(24))
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Visualization saved to: {output_path}")

    plt.close()

def plot_weather_vs_pm25(
    data,
    weather_parameter,
    output_path
):
    """
    Plot the relationship between a weather parameter
    and PM2.5 using a scatter plot.
    """

    data = data.copy()

    data = data[
        data["pm25"].notna() &
        data[weather_parameter].notna()
    ]

    plt.figure(figsize=(10, 6))

    plt.scatter(
        data[weather_parameter],
        data["pm25"],
        alpha=0.6
    )

    plt.xlabel(weather_parameter.replace("_", " ").title())
    plt.ylabel("PM2.5 (µg/m³)")

    plt.title(
        f"PM2.5 vs {weather_parameter.replace('_', ' ').title()}"
    )

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Visualization saved to: {output_path}")

    plt.close()


if __name__ == "__main__":

    input_path = "data/processed/openaq_measurements_transformed.csv"

    # Load transformed data
    df = pd.read_csv(input_path)

    # -----------------------------
    # Daily PM10
    # -----------------------------

    pm10_daily = daily_pollution_trend(
        df,
        parameter="pm10",
        unit="µg/m³"
    )

    plot_daily_pollution_trend(
        pm10_daily,
        parameter="pm10",
        output_path="reports/daily_pm10_trend.png"
    )

    # -----------------------------
    # Hourly PM2.5
    # -----------------------------

    pm25_hourly = hourly_pollution_pattern(
        df,
        parameter="pm25",
        unit="µg/m³"
    )

    plot_hourly_pollution_pattern(
        pm25_hourly,
        parameter="pm25",
        output_path="reports/hourly_pm25_pattern.png"
    )

    # -----------------------------
    # Hourly PM2.5 - Outlier Comparison
    # -----------------------------

    pm25_hourly_clean = hourly_pollution_pattern(
        df,
        parameter="pm25",
        unit="µg/m³",
        exclude_statistical_outliers=True
    )

    plot_pm25_outlier_comparison(
        pm25_hourly,
        pm25_hourly_clean,
        output_path="reports/hourly_pm25_outlier_comparison.png"
    )
    # -----------------------------
    # Weather vs PM2.5
    # -----------------------------

    weather_data = create_weather_pollution_dataset(df)

    plot_weather_vs_pm25(
        weather_data,
        weather_parameter="temperature",
        output_path="reports/pm25_vs_temperature.png"
    )
    plot_weather_vs_pm25(
        weather_data,
        weather_parameter="relativehumidity",
        output_path="reports/pm25_vs_relativehumidity.png"
    )
    plot_weather_vs_pm25(
        weather_data,
        weather_parameter="wind_speed",
        output_path="reports/pm25_vs_wind_speed.png"
    )