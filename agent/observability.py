import json
import tempfile
from pathlib import Path
import time

import mlflow

from config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME


def setup_mlflow():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def start_timer():
    return time.perf_counter()


def elapsed_ms(start_time):
    return int((time.perf_counter() - start_time) * 1000)


def log_json_artifact(filename: str, payload):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        mlflow.log_artifact(str(path))


def log_text_artifact(filename: str, text: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        path.write_text(text or "", encoding="utf-8")
        mlflow.log_artifact(str(path))