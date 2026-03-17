import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from src.forecast import find_subproject_timestamp, parse_datetime, pick_latest_subproject
except ModuleNotFoundError:
    PROJECT_SRC_ROOT = Path(__file__).resolve().parents[1].joinpath("dhi-ghm-downloader")
    if str(PROJECT_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_SRC_ROOT))
    from src.forecast import find_subproject_timestamp, parse_datetime, pick_latest_subproject


class TestForecast(unittest.TestCase):
    def test_parse_datetime_none_and_invalid(self) -> None:
        self.assertIsNone(parse_datetime(None))
        self.assertIsNone(parse_datetime("   "))
        self.assertIsNone(parse_datetime("not-a-date"))

    def test_parse_datetime_timestamp_inputs(self) -> None:
        naive = pd.Timestamp("2026-03-16 10:00:00")
        aware = pd.Timestamp("2026-03-16T10:00:00+01:00")

        self.assertEqual(str(parse_datetime(naive).tz), "UTC")
        self.assertEqual(parse_datetime(aware), pd.Timestamp("2026-03-16T09:00:00Z"))

    def test_parse_datetime_datetime_inputs(self) -> None:
        naive = datetime(2026, 3, 16, 10, 0, 0)
        aware = datetime(2026, 3, 16, 10, 0, 0, tzinfo=timezone.utc)

        self.assertEqual(parse_datetime(naive), pd.Timestamp("2026-03-16T10:00:00Z"))
        self.assertEqual(parse_datetime(aware), pd.Timestamp("2026-03-16T10:00:00Z"))

    def test_parse_datetime_epoch_seconds_and_millis(self) -> None:
        self.assertEqual(parse_datetime(1710000000), pd.Timestamp(1710000000, unit="s", tz="UTC"))
        self.assertEqual(parse_datetime(1710000000000), pd.Timestamp(1710000000, unit="s", tz="UTC"))

    def test_parse_datetime_string_formats(self) -> None:
        cases = [
            "2026-03-16T10:00:00Z",
            "2026-03-16 10:00:00",
            "2026-03-16",
            "2026031610",
            "20260316",
        ]
        for value in cases:
            with self.subTest(value=value):
                parsed = parse_datetime(value)
                self.assertIsInstance(parsed, pd.Timestamp)
                self.assertEqual(str(parsed.tz), "UTC")

    def test_find_subproject_timestamp(self) -> None:
        subproject = {"name": "x", "createdAt": "2026-03-16T10:00:00Z"}
        ts = find_subproject_timestamp(subproject)
        self.assertEqual(ts, pd.Timestamp("2026-03-16T10:00:00Z"))

    def test_pick_latest_subproject(self) -> None:
        subprojects = [
            {"id": "a", "forecastTimestamp": "2026-03-15T10:00:00Z"},
            {"id": "b", "forecastTimestamp": "2026-03-16T10:00:00Z"},
            {"id": "c", "forecastTimestamp": "2026-03-14T10:00:00Z"},
        ]
        latest, ts = pick_latest_subproject(subprojects)
        self.assertEqual(latest["id"], "b")
        self.assertEqual(ts, pd.Timestamp("2026-03-16T10:00:00Z"))

    def test_pick_latest_subproject_raises_without_timestamps(self) -> None:
        with self.assertRaises(ValueError):
            pick_latest_subproject([{"id": "a"}, {"id": "b"}])


if __name__ == "__main__":
    unittest.main()
