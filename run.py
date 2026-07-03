import argparse
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )


def write_metrics(output_path, metrics):
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Minimal MLOps batch job")
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    setup_logging(args.log_file)
    start_time = time.time()
    version = "unknown"

    try:
        logging.info("Job started")

        if not Path(args.config).exists():
            raise FileNotFoundError("Config file not found")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Invalid config structure")

        for key in ["seed", "window", "version"]:
            if key not in config:
                raise ValueError(f"Missing required config field: {key}")

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window must be a positive integer")

        np.random.seed(seed)
        logging.info(f"Config loaded and validated: seed={seed}, window={window}, version={version}")

        if not Path(args.input).exists():
            raise FileNotFoundError("Input file not found")

# Read CSV
        df = pd.read_csv(args.input)

# Check if file is empty
        if df.empty:
            raise ValueError("Input CSV is empty")
# Fix CSV if entire row is read as one column
        if len(df.columns) == 1 and "," in df.columns[0]:
            fixed_df = df.iloc[:, 0].str.split(",", expand=True)
            fixed_df.columns = df.columns[0].split(",")
            df = fixed_df
# Convert all column names to lowercase
        df.columns = df.columns.str.lower()

# Check if 'close' column exists
        if "close" not in df.columns:
            raise ValueError("Missing required column: close")

# Convert numeric columns to numeric datatype
        numeric_cols = [
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        logging.info(f"Rows loaded: {len(df)}")

        df["rolling_mean"] = df["close"].rolling(window=window).mean()
        logging.info("Rolling mean calculated")

        df["signal"] = np.where(df["close"] > df["rolling_mean"], 1, 0)
        logging.info("Signal generated")

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": int(len(df)),
            "metric": "signal_rate",
            "value": round(float(df["signal"].mean()), 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success",
        }

        write_metrics(args.output, metrics)
        logging.info(f"Metrics summary: {metrics}")
        logging.info("Job ended with status: success")

        print(json.dumps(metrics, indent=4))
        return 0

    except Exception as e:
        logging.exception("Job failed")

        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": str(e),
        }

        write_metrics(args.output, error_metrics)
        print(json.dumps(error_metrics, indent=4))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())