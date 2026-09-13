import pandas as pd

df = pd.read_csv("data/raw/openaq_measurements.csv")

print("Shape:", df.shape)

print("Columns:")
print(df.columns)

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())
print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nParameters:")
print(df["parameter"].value_counts())

print("\nParameter and Units:")
print(df.groupby(["parameter", "unit"]).size())

print("\nLocations:")
print(df["location_name"].value_counts())

print("\nDate Range:")
print("UTC:", df["datetimeUtc"].min(), "to", df["datetimeUtc"].max())
print("Local:", df["datetimeLocal"].min(), "to", df["datetimeLocal"].max())

print("\nValue Statistics by Parameter:")
print(df.groupby("parameter")["value"].describe())

print("\nHighest PM10 values:")
print(
    df[df["parameter"] == "pm10"]
    .sort_values("value", ascending=False)
    .head(10)
)

print("\nHighest PM10 values:")

pm10_high = (
    df[df["parameter"] == "pm10"]
    .sort_values("value", ascending=False)
    .head(10)
)

print(
    pm10_high[
        ["value", "unit", "datetimeLocal", "datetimeUtc"]
    ]
)

print("\nParameter Value Range:")

print(
    df.groupby(["parameter", "unit"])["value"]
    .agg(["min", "max"])
)

print("\nHighest Wind Speed values:")

wind_high = (
    df[df["parameter"] == "wind_speed"]
    .sort_values("value", ascending=False)
    .head(10)
)

print(
    wind_high[
        ["value", "unit", "datetimeLocal", "datetimeUtc"]
    ]
)

print("\nWind Speed Around Anomaly:")

wind_anomaly = df[
    (df["parameter"] == "wind_speed") &
    (df["datetimeLocal"].str.startswith("2025-02-19"))
]

print(
    wind_anomaly[
        ["value", "unit", "datetimeLocal", "datetimeUtc"]
    ].sort_values("datetimeLocal")
)

print("\nTimestamp Intervals:")

wind = (
    df[df["parameter"] == "wind_speed"]
    .copy()
)

wind["datetimeLocal"] = pd.to_datetime(wind["datetimeLocal"])

wind = wind.sort_values("datetimeLocal")

print(
    wind["datetimeLocal"]
    .diff()
    .value_counts()
)

print("\nRecords by Parameter and Date:")

df["date"] = pd.to_datetime(df["datetimeLocal"]).dt.date

print(
    df.groupby(["parameter", "date"])
    .size()
    .head(20)
)

print("\nDate Coverage:")

date_summary = (
    df.groupby("date")
    .size()
)

print("Number of dates with data:", date_summary.shape[0])
print("First 10 dates:")
print(date_summary.head(10))

print("\nLast 10 dates:")
print(date_summary.tail(10))

print("\nDate Coverage:")

print("\nDate Coverage:")

date_summary = df.groupby("date").size()

print("Number of dates with data:", date_summary.shape[0])

print("\nFirst 10 dates:")
print(date_summary.head(10))

print("\nLast 10 dates:")
print(date_summary.tail(10))