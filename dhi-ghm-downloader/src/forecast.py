"""Helpers to detect and select latest forecast subproject."""

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

TIMESTAMP_FIELDS = [
    "forecastTimestamp",
    "forecastTime",
    "forecastDate",
    "createdAt",
    "updatedAt",
    "timestamp",
]


def parse_datetime(value: Any) -> Optional[pd.Timestamp]:
    """Parse an input value into a UTC pandas Timestamp when possible."""
    if value is None:
        return None

    if isinstance(value, pd.Timestamp):
        return value.tz_convert("UTC") if value.tzinfo else value.tz_localize("UTC")

    if isinstance(value, datetime):
        as_ts = pd.Timestamp(value)
        return as_ts.tz_convert("UTC") if as_ts.tzinfo else as_ts.tz_localize("UTC")

    if isinstance(value, (int, float)):
        epoch = float(value)
        if epoch > 1e11:
            epoch /= 1000.0
        return pd.to_datetime(epoch, unit="s", utc=True)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None

        parsed = pd.to_datetime(text.replace("Z", "+00:00"), utc=True, errors="coerce")
        if not pd.isna(parsed):
            return parsed

        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d%H", "%Y%m%d"]:
            try:
                return pd.to_datetime(text, format=fmt, utc=True)
            except ValueError:
                continue

    return None


def find_subproject_timestamp(subproject: Dict[str, Any]) -> Optional[pd.Timestamp]:
    """Find the first valid forecast timestamp field in a subproject payload."""
    for field in TIMESTAMP_FIELDS:
        if field in subproject:
            timestamp = parse_datetime(subproject.get(field))
            if timestamp:
                return timestamp
    return None


def pick_latest_subproject(subprojects: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Any], pd.Timestamp]:
    """Pick the newest subproject based on the detected timestamp fields."""
    ranked: List[Tuple[pd.Timestamp, Dict[str, Any]]] = []

    for subproject in subprojects:
        timestamp = find_subproject_timestamp(subproject)
        if timestamp:
            ranked.append((timestamp, subproject))

    if not ranked:
        fields = ", ".join(TIMESTAMP_FIELDS)
        raise ValueError(f"No timestamp found on subprojects. Checked: {fields}")

    ranked.sort(key=lambda item: item[0], reverse=True)
    latest_timestamp, latest_subproject = ranked[0]
    return latest_subproject, latest_timestamp
