import argparse
import os
import subprocess
import sys


def run_command(command):
    """
    Run a Python script and stop the pipeline
    if the script fails.
    """

    print("\nRunning:", " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}"
        )



def parse_arguments():
    """
    Parse command-line arguments for the pipeline.
    """

    parser = argparse.ArgumentParser(
        description="Run the Bengaluru air quality data pipeline"
    )

    parser.add_argument(
        "--location",
        type=int,
        default=6973,
        help="OpenAQ location ID"
    )

    parser.add_argument(
        "--from-date",
        default="2025-02-19T00:00:00Z",
        help="Start datetime in ISO 8601 format"
    )

    parser.add_argument(
        "--to-date",
        default="2025-02-20T00:00:00Z",
        help="End datetime in ISO 8601 format"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    location_id = args.location
    date_from = args.from_date
    date_to = args.to_date

    start_date = date_from[:10]
    end_date = date_to[:10]

    raw_file = (
        f"data/raw/"
        f"openaq_sensor_{location_id}_"
        f"{start_date}_{end_date}.csv"
    )

    run_command([
        sys.executable,
        "src/api_ingestion.py",
        "--location", str(location_id),
        "--from-date", date_from,
        "--to-date", date_to
    ])
    if not os.path.exists(raw_file):
        raise FileNotFoundError(
            f"Raw data file was not created: {raw_file}"
        )

    print(f"Raw data file validated: {raw_file}")

    run_command([
        sys.executable,
        "src/transform_data.py",
        "--input",
        raw_file
    ])
    processed_file = (
        f"data/processed/"
        f"openaq_measurements_{start_date}_{end_date}.csv"
    )

    if not os.path.exists(processed_file):
        raise FileNotFoundError(
            f"Processed data file was not created: {processed_file}"
        )

    print(f"Processed data file validated: {processed_file}")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()