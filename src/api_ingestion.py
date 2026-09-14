import os
import requests
import pandas as pd
from dotenv import load_dotenv
import logging
import time
import argparse
from dotenv import load_dotenv

BASE_URL = "https://api.openaq.org/v3"
API_TIMEOUT = int(os.getenv("OPENAQ_API_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("OPENAQ_MAX_RETRIES", "3"))
PAGE_SIZE = int(os.getenv("OPENAQ_PAGE_SIZE", "1000"))
LOCATION_ID = int(os.getenv("OPENAQ_LOCATION_ID", "6973"))

DATE_FROM = os.getenv("OPENAQ_DATE_FROM", "2025-02-19T00:00:00Z")
DATE_TO = os.getenv("OPENAQ_DATE_TO", "2025-02-20T00:00:00Z")

# Load variables from .env
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)



def get_api_key():
    """
    Retrieve the OpenAQ API key from environment variables.
    """

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    return api_key


def api_get(endpoint, params=None, max_retries=MAX_RETRIES):
    """
    Send a GET request to the OpenAQ API.

    Retries temporary network/server failures before
    raising an error.
    """

    url = f"{BASE_URL}{endpoint}"

    headers = {
        "X-API-Key": get_api_key()
    }

    for attempt in range(1, max_retries + 1):

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=API_TIMEOUT
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:

            logger.warning(
                f"Request timed out "
                f"(attempt {attempt}/{max_retries})"
            )

            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))

        except requests.exceptions.ConnectionError:

            logger.warning(
                f"Connection error "
                f"(attempt {attempt}/{max_retries})"
            )

            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))

        except requests.exceptions.HTTPError as error:

            if response.status_code == 429:

                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    wait_time = int(retry_after)
                else:
                    wait_time = 2 ** (attempt - 1)

                logger.warning(
                    f"Rate limit exceeded "
                    f"(attempt {attempt}/{max_retries}). "
                    f"Waiting {wait_time} seconds."
                )

                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue

            logger.error(
                f"HTTP error: {error} "
                f"(attempt {attempt}/{max_retries})"
            )

            raise

    raise RuntimeError(
        f"API request failed after {max_retries} attempts"
    )

def get_location(location_id):
    """
    Retrieve metadata for an OpenAQ location.
    """

    return api_get(f"/locations/{location_id}")

def get_sensors(location_id):
    """
    Retrieve sensor metadata for an OpenAQ location.
    """

    return api_get(f"/locations/{location_id}/sensors")

def get_active_sensors(location_id):
    """
    Retrieve sensors available for a location.

    Returns the sensor records from the OpenAQ API.
    """

    sensors_response = get_sensors(location_id)

    sensors = sensors_response.get("results", [])

    logger.info(
        f"Found {len(sensors)} sensor(s) "
        f"for location {location_id}"
    )

    return sensors

def select_sensors(sensors):
    """
    Select sensors that should be included in the ingestion pipeline.

    Currently selects one sensor for each parameter/unit
    combination.
    """

    selected = {}
    duplicate_sensors = []

    for sensor in sensors:

        parameter = sensor.get("parameter", {})
        parameter_name = parameter.get("name")
        unit = parameter.get("units")

        key = (parameter_name, unit)

        if key not in selected:
            selected[key] = sensor

        else:
            duplicate_sensors.append(sensor)

    logger.info(
        f"Selected {len(selected)} unique "
        f"parameter/unit sensor combinations"
    )

    logger.info(
        f"Skipped {len(duplicate_sensors)} duplicate sensor(s)"
    )

    return list(selected.values())

def ingest_location(location_id, date_from, date_to):
    """
    Ingest measurements from all selected sensors
    for a location within a date range.
    """

    logger.info(
        f"Starting location ingestion for {location_id}"
    )

    location = get_location(location_id)

    sensors = get_active_sensors(location_id)

    selected_sensors = select_sensors(sensors)

    all_data = []

    for sensor in selected_sensors:

        sensor_id = sensor["id"]

        logger.info(
            f"Ingesting sensor {sensor_id}: "
            f"{sensor['name']}"
        )

        df = ingest_sensor_measurements(
            sensor_id,
            date_from,
            date_to
        )

        if df.empty:
            logger.warning(
                f"No measurements found for sensor {sensor_id}"
            )
            continue

        flattened_df = flatten_measurements(df)

        enriched_df = enrich_measurements(
            flattened_df,
            location,
            sensor_id
        )

        all_data.append(enriched_df)

    if not all_data:
        logger.warning(
            f"No measurement data found for location {location_id}"
        )
        return pd.DataFrame()

    combined_df = pd.concat(
        all_data,
        ignore_index=True
    )

    logger.info(
        f"Location ingestion completed: "
        f"{len(combined_df)} total measurements"
    )

    return combined_df

def get_measurements(sensor_id, date_from, date_to):
    """
    Retrieve all measurements for a sensor within a date range.

    Uses pagination to retrieve all available records.
    """

    all_measurements = []
    page = 1
    limit = PAGE_SIZE

    while True:

        params = {
            "datetime_from": date_from,
            "datetime_to": date_to,
            "limit": limit,
            "page": page
        }

        response = api_get(
            f"/sensors/{sensor_id}/measurements",
            params=params
        )

        results = response.get("results", [])

        all_measurements.extend(results)

        logger.info(
            f"Page {page}: "
            f"{len(results)} measurements retrieved"
        )

        # Stop when the API returns fewer records
        # than the requested page size.
        if len(results) < limit:
            break

        page += 1

    return all_measurements

def ingest_sensor_measurements(sensor_id, date_from, date_to):
    """
    Ingest measurements for a sensor within a date range.

    Retrieves all measurements from the OpenAQ API and
    converts the results into a Pandas DataFrame.
    """

    logger.info(
        f"Starting ingestion for sensor {sensor_id} "
        f"from {date_from} to {date_to}"
    )

    measurements = get_measurements(
        sensor_id,
        date_from,
        date_to
    )

    logger.info(
        f"Total measurements retrieved: {len(measurements)}"
    )

    df = pd.DataFrame(measurements)

    logger.info(
        f"Created DataFrame with {len(df)} rows"
    )

    return df

def flatten_measurements(df):
    """
    Flatten nested OpenAQ measurement fields into
    a tabular DataFrame.
    """

    flattened = pd.DataFrame()

    flattened["value"] = df["value"]

    flattened["parameter"] = df["parameter"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else None
    )

    flattened["unit"] = df["parameter"].apply(
        lambda x: x.get("units") if isinstance(x, dict) else None
    )

    flattened["datetime_utc"] = df["period"].apply(
        lambda x: x["datetimeFrom"]["utc"]
        if isinstance(x, dict)
        else None
    )

    flattened["datetime_local"] = df["period"].apply(
        lambda x: x["datetimeFrom"]["local"]
        if isinstance(x, dict)
        else None
    )

    return flattened

def enrich_measurements(df, location, sensor_id):
    """
    Add location and sensor metadata to the flattened
    measurement DataFrame.
    """

    results = location.get("results", [])

    if not results:
        raise ValueError("Location metadata not found")

    location_data = results[0]

    enriched = df.copy()

    enriched["sensor_id"] = sensor_id

    enriched["location_id"] = location_data.get("id")
    enriched["location_name"] = location_data.get("name")
    enriched["timezone"] = location_data.get("timezone")

    coordinates = location_data.get("coordinates", {})

    enriched["latitude"] = coordinates.get("latitude")
    enriched["longitude"] = coordinates.get("longitude")

    country = location_data.get("country", {})
    enriched["country_iso"] = country.get("code")

    enriched["is_mobile"] = location_data.get("isMobile")
    enriched["is_monitor"] = location_data.get("isMonitor")

    owner = location_data.get("owner", {})
    enriched["owner_name"] = owner.get("name")

    provider = location_data.get("provider", {})
    enriched["provider"] = provider.get("name")

    return enriched

def save_raw_data(df, sensor_id, date_from, date_to):
    """
    Save ingested data to the raw data directory.

    The filename is generated dynamically using the
    sensor ID and ingestion date range.
    """

    raw_dir = "data/raw"

    os.makedirs(raw_dir, exist_ok=True)

    start_date = date_from[:10]
    end_date = date_to[:10]

    filename = (
        f"openaq_sensor_{sensor_id}_"
        f"{start_date}_{end_date}.csv"
    )

    file_path = os.path.join(raw_dir, filename)

    df.to_csv(file_path, index=False)

    logger.info(
        f"Raw data saved to {file_path} "
        f"({len(df)} rows)"
    )

    return file_path
def get_location_flags(location_id, date_from, date_to):
    """
    Retrieve data-quality flags for an OpenAQ location
    within a specified date range.
    """

    params = {
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": 100
    }

    return api_get(
        f"/locations/{location_id}/flags",
        params=params
    )


def find_wind_sensors(location_id):
    """
    Find all wind-speed sensors for an OpenAQ location.
    """

    sensors_response = get_sensors(location_id)

    wind_sensors = [
        sensor
        for sensor in sensors_response.get("results", [])
        if sensor.get("parameter", {}).get("name") == "wind_speed"
    ]

    logger.info(
        f"Found {len(wind_sensors)} wind-speed sensor(s) "
        f"for location {location_id}"
    )

    return wind_sensors

def parse_arguments():
    """
    Parse command-line arguments for location and date range.
    """

    parser = argparse.ArgumentParser(
        description="Ingest air quality data from OpenAQ"
    )

    parser.add_argument(
        "--location",
        type=int,
        default=LOCATION_ID,
        help="OpenAQ location ID"
    )

    parser.add_argument(
        "--from-date",
        default=DATE_FROM,
        help="Start datetime in ISO 8601 format"
    )

    parser.add_argument(
        "--to-date",
        default=DATE_TO,
        help="End datetime in ISO 8601 format"
    )

    return parser.parse_args()

def main():
    """
    Run the OpenAQ location ingestion workflow
    using command-line arguments.
    """

    args = parse_arguments()

    combined_df = ingest_location(
        args.location,
        args.from_date,
        args.to_date
    )

    print("\nCombined DataFrame shape:")
    print(combined_df.shape)

    print("\nMeasurements by parameter:")

    print(
        combined_df.groupby(
            ["parameter", "unit"]
        ).size()
    )

    print("\nFirst 5 records:")
    print(combined_df.head())

    if not combined_df.empty:

        output_file = save_raw_data(
            combined_df,
            args.location,
            args.from_date,
            args.to_date
        )

        print("\nRaw data saved to:")
        print(output_file)

if __name__ == "__main__":
    main()