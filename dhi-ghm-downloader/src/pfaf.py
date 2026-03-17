"""Helpers for parsing PFAF ID inputs."""

import json
from pathlib import Path
from typing import List, Optional


def parse_pfaf_ids(cli_values: List[str], pfaf_file: Optional[str]) -> List[str]:
    values: List[str] = []

    for item in cli_values:
        text = str(item).strip()
        if not text:
            continue

        if text.startswith("[") and text.endswith("]"):
            parsed = json.loads(text.replace("'", '"'))
            if not isinstance(parsed, list):
                raise ValueError("--pfaf-ids list format must be a JSON list")
            values.extend([str(v).strip() for v in parsed if str(v).strip()])
        else:
            values.append(text)

    if pfaf_file:
        file_text = Path(pfaf_file).read_text(encoding="utf-8")
        tokens = [token.strip() for token in file_text.replace("\n", ",").split(",")]
        values.extend([token for token in tokens if token])

    unique: List[str] = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)

    if not unique:
        raise ValueError("Provide PFAF IDs with --pfaf-ids and/or --pfaf-file")

    return unique
