"""DataFrame conversion helpers for GHM timeseries payloads."""

from typing import Any, Dict, List, Optional

import pandas as pd


def extract_timeseries_items(payload: Any) -> List[Dict[str, Any]]:
    """Extract timeseries dictionaries from API payload variations."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("timeseries", "items", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

        if all(isinstance(value, dict) for value in payload.values()):
            return [value for value in payload.values() if isinstance(value, dict)]

    raise ValueError("Unexpected response format from bulk ghm-timeseries endpoint")


def find_timeseries_id(payload: Dict[str, Any]) -> Optional[str]:
    """Read a timeseries identifier from a payload or metadata block."""
    for key in ("tsId", "id"):
        value = payload.get(key)
        if value is not None:
            return str(value)

    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        for key in ("tsId", "id"):
            value = metadata.get(key)
            if value is not None:
                return str(value)

    return None


def map_timeseries_items(payload: Any) -> Dict[str, Dict[str, Any]]:
    """Create a lookup map of timeseries items by tsId."""
    if isinstance(payload, dict) and all(isinstance(v, dict) for v in payload.values()):
        return {str(k): v for k, v in payload.items()}

    item_map: Dict[str, Dict[str, Any]] = {}
    for item in extract_timeseries_items(payload):
        ts_id = find_timeseries_id(item)
        if ts_id:
            item_map[ts_id] = item
    return item_map


def timeseries_dict_to_dataframe(ts_payload: Dict[str, Any]) -> pd.DataFrame:
    """Convert a timeseries dictionary payload into a typed pandas DataFrame."""
    date_times = ts_payload.get("dateTimes", []) or []
    values = ts_payload.get("values", []) or []

    if len(date_times) != len(values):
        raise ValueError("Timeseries payload has mismatched dateTimes/values lengths")

    df = pd.DataFrame({"dateTimes": date_times, "values": values})
    df["dateTimes"] = pd.to_datetime(df["dateTimes"], utc=True, errors="coerce")

    if df["dateTimes"].isna().any():
        raise ValueError("Timeseries payload contains invalid dateTimes values")

    df["values"] = pd.to_numeric(df["values"], errors="coerce")
    return df
