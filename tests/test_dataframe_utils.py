import sys
import unittest
from pathlib import Path

import pandas as pd

try:
    from src.dataframe_utils import (
        extract_timeseries_items,
        find_timeseries_id,
        map_timeseries_items,
        timeseries_dict_to_dataframe,
    )
except ModuleNotFoundError:
    PROJECT_SRC_ROOT = Path(__file__).resolve().parents[1].joinpath("dhi-ghm-downloader")
    if str(PROJECT_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_SRC_ROOT))
    from src.dataframe_utils import (
        extract_timeseries_items,
        find_timeseries_id,
        map_timeseries_items,
        timeseries_dict_to_dataframe,
    )


class TestDataframeUtils(unittest.TestCase):
    def test_extract_timeseries_items_from_list(self) -> None:
        payload = [{"id": 1}, "x", {"id": 2}]
        self.assertEqual(extract_timeseries_items(payload), [{"id": 1}, {"id": 2}])

    def test_extract_timeseries_items_from_dict_list_keys(self) -> None:
        payload = {"items": [{"id": 1}, {"id": 2}]}
        self.assertEqual(extract_timeseries_items(payload), [{"id": 1}, {"id": 2}])

    def test_extract_timeseries_items_from_dict_values(self) -> None:
        payload = {"a": {"id": 1}, "b": {"id": 2}}
        self.assertEqual(extract_timeseries_items(payload), [{"id": 1}, {"id": 2}])

    def test_extract_timeseries_items_raises(self) -> None:
        with self.assertRaises(ValueError):
            extract_timeseries_items("bad")

    def test_find_timeseries_id(self) -> None:
        self.assertEqual(find_timeseries_id({"tsId": 123}), "123")
        self.assertEqual(find_timeseries_id({"id": "abc"}), "abc")
        self.assertEqual(find_timeseries_id({"metadata": {"tsId": "m1"}}), "m1")
        self.assertIsNone(find_timeseries_id({"metadata": {}}))

    def test_map_timeseries_items(self) -> None:
        as_dict = {"1": {"v": 1}, "2": {"v": 2}}
        self.assertEqual(map_timeseries_items(as_dict), as_dict)

        payload = [
            {"tsId": "10", "dateTimes": [], "values": []},
            {"metadata": {"id": "11"}, "dateTimes": [], "values": []},
            {"name": "no-id"},
        ]
        mapped = map_timeseries_items(payload)
        self.assertIn("10", mapped)
        self.assertIn("11", mapped)
        self.assertNotIn("no-id", mapped)

    def test_timeseries_dict_to_dataframe(self) -> None:
        payload = {
            "dateTimes": ["2026-03-16T10:00:00Z", "2026-03-16T11:00:00Z"],
            "values": ["1.25", 2],
        }
        df = timeseries_dict_to_dataframe(payload)

        self.assertEqual(len(df), 2)
        self.assertIsInstance(df.loc[0, "dateTimes"], pd.Timestamp)
        self.assertEqual(str(df.loc[0, "dateTimes"].tz), "UTC")
        self.assertAlmostEqual(df.loc[0, "values"], 1.25)

    def test_timeseries_dict_to_dataframe_mismatched_lengths(self) -> None:
        with self.assertRaises(ValueError):
            timeseries_dict_to_dataframe({"dateTimes": ["2026-03-16T10:00:00Z"], "values": []})

    def test_timeseries_dict_to_dataframe_invalid_datetime(self) -> None:
        with self.assertRaises(ValueError):
            timeseries_dict_to_dataframe({"dateTimes": ["bad-date"], "values": [1]})


if __name__ == "__main__":
    unittest.main()
