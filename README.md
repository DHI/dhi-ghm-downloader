# Latest Forecast Downloader (2DMI)

Standalone client package to download only the latest forecast timeseries for a list of PFAF IDs.

## What it does

1. Calls `/subProjectIds` for the root project:
   - `194fb871-086d-4117-9d70-119af3b80111` (default)
2. Picks the subproject with the largest timestamp (latest forecast).
3. Calls `/ghm-timeseries/{tsId}` for each PFAF ID.
4. Saves each series to CSV in the output folder.

## Files

- `download_latest_forecast.py` : standalone script
- `forecast_downloader/` : extracted reusable methods
- `pixi.toml` : Pixi environment and run tasks
- `requirements.txt` : optional pip dependency file

## Setup

```bash
pixi install
```

## Run

Use space-separated PFAF IDs:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --pfaf-ids 136320200000 219730300000
```

Use list-style PFAF IDs:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --pfaf-ids "[136320200000,219730300000]"
```

Use PFAF IDs from file:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --pfaf-file pfaf_ids_example.txt
```

Alternative predefined task:

```bash
pixi run download --api-key <YOUR_API_KEY> --pfaf-file pfaf_ids_example.txt
```

Optional arguments:

- `--project-id` (default: `194fb871-086d-4117-9d70-119af3b80111`)
- `--base-url`
- `--environment` (default: `prod`)
- `--timeout` (default: `60`)
- `--outdir` (default: `output_latest_forecast`)
