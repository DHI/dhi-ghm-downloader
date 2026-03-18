#!/usr/bin/env python
"""Download the latest forecast timeseries for selected PFAF IDs.

API flow:
1) GET /subProjectIds using the root project ID
2) Select the forecast with the biggest timestamp
3) POST /ghm-timeseries/tsIds for all requested PFAF IDs

Examples:
    python download_latest_forecast.py --api-key <KEY> --pfaf-ids "[136320200000,219730300000]"
    python download_latest_forecast.py --api-key <KEY> --pfaf-ids 136320200000 219730300000
  python download_latest_forecast.py --api-key <KEY> --pfaf-file pfaf_ids.txt
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

try:
    from src.api import ApiClient, ApiSettings
    from src.dataframe_utils import map_timeseries_items, timeseries_dict_to_dataframe
    from src.forecast import pick_latest_subproject
    from src.pfaf import parse_pfaf_ids
except ModuleNotFoundError:
    PROJECT_PACKAGE_ROOT = Path(__file__).resolve().parent.joinpath("dhi-ghm-downloader")
    if str(PROJECT_PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_PACKAGE_ROOT))
    from src.api import ApiClient, ApiSettings
    from src.dataframe_utils import map_timeseries_items, timeseries_dict_to_dataframe
    from src.forecast import pick_latest_subproject
    from src.pfaf import parse_pfaf_ids

DEFAULT_BASE_URL = "https://wrd-mike-cloud-performance-statistics.azurewebsites.net/api"
DEFAULT_ENVIRONMENT = "prod"
DEFAULT_TIMEOUT = 60


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for latest forecast download."""
    parser = argparse.ArgumentParser(
        description=(
            "Download latest forecast timeseries for a list of PFAF IDs. "
            "Latest forecast is selected from the newest timestamped subproject."
        )
    )
    parser.add_argument("--api-key", required=True, help="API key (dhiOpenApiKey).")
    parser.add_argument(
        "--project-id",
        required=True,
        help="Root project ID used for /subProjectIds.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL.")
    parser.add_argument(
        "--environment",
        default=DEFAULT_ENVIRONMENT,
        help="Environment query parameter.",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds."
    )

    parser.add_argument(
        "--pfaf-ids",
        nargs="+",
        default=[],
        help=(
            "PFAF IDs as space-separated values (e.g. 136320200000 219730300000) "
            "or as one list string (e.g. '[136320200000,219730300000]'). "
            "Required unless --pfaf-file is provided."
        ),
    )
    parser.add_argument(
        "--pfaf-file",
        default=None,
        help=(
            "Text file containing PFAF IDs separated by comma/newline. "
            "Required unless --pfaf-ids is provided."
        ),
    )
    parser.add_argument(
        "--outdir",
        default="output_latest_forecast",
        help="Output directory for CSV files.",
    )
    return parser.parse_args()


def write_timeseries_csv(ts_payload: Dict[str, object], output_file: Path) -> int:
    """Write a single timeseries payload to CSV and return row count."""
    df = timeseries_dict_to_dataframe(ts_payload)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    return len(df)


def main() -> int:
    """Run the latest forecast download flow."""
    args = parse_args()

    try:
        pfaf_ids = parse_pfaf_ids(args.pfaf_ids, args.pfaf_file)
    except Exception as exc:
        print(f"Input error: {exc}")
        return 2

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    settings = ApiSettings(
        api_key=args.api_key,
        project_id=args.project_id,
        base_url=args.base_url,
        environment=args.environment,
        timeout=args.timeout,
    )
    client = ApiClient(settings)
    try:
        try:
            subprojects = client.get_subprojects()
        except Exception as exc:
            print(f"Failed to call /subProjectIds: {exc}")
            return 1

        if not isinstance(subprojects, list) or not subprojects:
            print("No subprojects returned by /subProjectIds")
            return 1

        try:
            latest, latest_timestamp = pick_latest_subproject(subprojects)
        except Exception as exc:
            print(f"Failed to select latest forecast subproject: {exc}")
            return 1

        latest_id = latest.get("id")
        if not latest_id:
            print("Latest subproject has no 'id'")
            return 1

        print(
            f"Latest forecast subproject: {latest.get('name', latest_id)} "
            f"({latest_id}) at {latest_timestamp.isoformat()}"
        )

        try:
            payload = client.get_timeseries_bulk(project_id=str(latest_id), ids=pfaf_ids)
            item_map = map_timeseries_items(payload)
        except Exception as exc:
            print(f"Failed to call bulk /ghm-timeseries/tsIds: {exc}")
            return 1

        success = 0
        for pfaf_id in pfaf_ids:
            try:
                ts_payload = item_map.get(pfaf_id)
                if ts_payload is None:
                    raise ValueError("Not returned by bulk endpoint")

                output_file = outdir.joinpath(f"{pfaf_id}.csv")
                points = write_timeseries_csv(ts_payload, output_file)
                success += 1
                print(f"Downloaded {pfaf_id}: {points} rows -> {output_file}")
            except Exception as exc:
                print(f"Failed {pfaf_id}: {exc}")

        print(f"Done: {success}/{len(pfaf_ids)} timeseries downloaded")
        return 0 if success > 0 else 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
