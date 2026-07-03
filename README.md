# Minimal MLOps Batch Job

## Overview

This project implements a simple MLOps-style batch processing pipeline in Python.

Features:
- Reads configuration from YAML
- Validates input dataset
- Computes rolling mean
- Generates binary trading signals
- Produces structured metrics
- Logs execution details
- Dockerized for reproducible execution

---

## Requirements

- Python 3.9+
- Docker Desktop

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Local Run

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Docker Build

```bash
docker build -t mlops-task .
```

---

## Docker Run

```bash
docker run --rm mlops-task
```

---

## Sample Output

```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4989,
    "latency_ms": 43,
    "seed": 42,
    "status": "success"
}
```