# Latest Forecast Downloader (2DMI)

Standalone tooling for downloading GHM timeseries data.

The repository currently includes a script for downloading the latest forecast for a list of PFAF IDs, and is structured so additional scripts can be added over time.

## What `download_latest_forecast.py` does

1. Calls `/subProjectIds` for the root project.
2. Picks the subproject with the largest timestamp (latest forecast).
3. Calls bulk `/ghm-timeseries/tsIds` for requested PFAF IDs.
4. Saves each series to CSV in the output folder.

## Repository Files

- `download_latest_forecast.py`: standalone CLI script for latest forecast download
- `dhi-ghm-downloader/src/`: reusable package modules (`api`, `forecast`, `pfaf`, dataframe helpers)
- `pixi.toml`: Pixi environment and run tasks
- `requirements.txt`: optional pip dependency file

## Setup

```bash
pixi install
```

## Run Latest Forecast Script

`--project-id` is required.

Use space-separated PFAF IDs:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --project-id <ROOT_PROJECT_ID> --pfaf-ids 136320200000 219730300000
```

Use list-style PFAF IDs:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --project-id <ROOT_PROJECT_ID> --pfaf-ids "[136320200000,219730300000]"
```

Use PFAF IDs from file:

```bash
pixi run python download_latest_forecast.py --api-key <YOUR_API_KEY> --project-id <ROOT_PROJECT_ID> --pfaf-file pfaf_ids_example.txt
```

Use predefined Pixi task:

```bash
pixi run download_latest --api-key <YOUR_API_KEY> --project-id <ROOT_PROJECT_ID> --pfaf-file pfaf_ids_example.txt
```

## Arguments

Required arguments:

- `--api-key`
- `--project-id`

Optional arguments:

- `--pfaf-ids`
- `--pfaf-file`
- `--base-url` (default: `https://wrd-mike-cloud-performance-statistics.azurewebsites.net/api`)
- `--environment` (default: `prod`)
- `--timeout` (default: `60`)
- `--outdir` (default: `output_latest_forecast`)

## Adding More Scripts in the Future

To keep Pixi usage consistent as more Python scripts are added:

1. Add the script at repository root (or preferred scripts folder).
2. Register a dedicated task in `pixi.toml`, for example:

```toml
[tasks]
download_latest = "python download_latest_forecast.py"
download_historical = "python download_historical_forecast.py"
```

3. Run with the same pattern:

```bash
pixi run <task_name> --<script-args>
```

Keep the generic `python = "python"` task for ad hoc script execution.
