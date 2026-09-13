import os
import requests
import pandas as pd
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()
print("API key loaded:", bool(os.getenv("OPENAQ_API_KEY")))

BASE_URL = "https://api.openaq.org/v3"


def get_location(location_id):
    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    url = f"{BASE_URL}/locations/{location_id}"

    headers = {
        "X-API-Key": api_key
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_sensors(location_id):
    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    url = f"{BASE_URL}/locations/{location_id}/sensors"

    headers = {
        "X-API-Key": api_key
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_measurements(sensor_id, date_from, date_to):
    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    url = f"{BASE_URL}/sensors/{sensor_id}/measurements"

    headers = {
        "X-API-Key": api_key
    }

    params = {
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": 1000
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_location_flags(location_id, date_from, date_to):
    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    url = f"{BASE_URL}/locations/{location_id}/flags"

    headers = {
        "X-API-Key": api_key
    }

    params = {
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": 100
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
def find_wind_sensors(location_id):
    sensors_response = get_sensors(location_id)

    wind_sensors = []

    for sensor in sensors_response["results"]:
        parameter = sensor["parameter"]["name"]

        if parameter == "wind_speed":
            wind_sensors.append(sensor)

    return wind_sensors
def get_location_measurements(location_id, date_from, date_to):

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY is not configured")

    url = f"{BASE_URL}/locations/{location_id}/measurements"

    headers = {
        "X-API-Key": api_key
    }

    params = {
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": 100
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
if __name__ == "__main__":

    measurements = get_location_measurements(
        6973,
        "2025-02-19T02:00:00Z",
        "2025-02-19T02:30:00Z"
    )

    print("\nLocation Measurements:")

    print(measurements)