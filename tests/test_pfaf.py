import sys
import tempfile
import unittest
from pathlib import Path

try:
    from src.pfaf import parse_pfaf_ids
except ModuleNotFoundError:
    PROJECT_SRC_ROOT = Path(__file__).resolve().parents[1].joinpath("dhi-ghm-downloader")
    if str(PROJECT_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_SRC_ROOT))
    from src.pfaf import parse_pfaf_ids


class TestPfaf(unittest.TestCase):
    def test_parse_pfaf_ids_from_cli_values(self) -> None:
        result = parse_pfaf_ids(["136", "219"], None)
        self.assertEqual(result, ["136", "219"])

    def test_parse_pfaf_ids_json_list(self) -> None:
        result = parse_pfaf_ids(["[136,219]"], None)
        self.assertEqual(result, ["136", "219"])

    def test_parse_pfaf_ids_with_file_and_dedup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir).joinpath("ids.txt")
            path.write_text("136,219\n136", encoding="utf-8")
            result = parse_pfaf_ids(["136", "300"], str(path))
            self.assertEqual(result, ["136", "300", "219"])

    def test_parse_pfaf_ids_raises_when_empty(self) -> None:
        with self.assertRaises(ValueError):
            parse_pfaf_ids([], None)


if __name__ == "__main__":
    unittest.main()
