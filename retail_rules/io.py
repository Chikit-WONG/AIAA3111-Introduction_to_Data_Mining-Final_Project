"""Small, explicit persistence helpers. All paths are repository-relative."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | Path = "configs/experiment.json") -> dict:
    p = Path(path)
    return json.loads((p if p.is_absolute() else ROOT / p).read_text(encoding="utf-8"))


def _json_default(obj):
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    if isinstance(obj, (Path, pd.Timestamp)):
        return str(obj)
    raise TypeError(type(obj).__name__)


def save_json(value, path: str | Path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=_json_default, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_csv(df: pd.DataFrame, path: str | Path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, float_format="%.12g")
