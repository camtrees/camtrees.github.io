#!/usr/bin/env python3
"""Export approved public database views to static JSON files.

Add a new entry to EXPORTS when another public view is ready.  Keeping the
allow-list here avoids accepting arbitrary table or SQL names from input.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parents[1]

CAM_TREE_COLUMNS = (
    "site",
    "tree_id",
    "cam_org",
    "hub",
    "date_planted_or_observed(wild)",
    "planted_by",
    "primary_caretaker",
    "secondary_caretaker",
    "latest_health",
    "latest_health_date",
    "latest_height_in_inches",
    "latest_height",
    "latest_height_date",
    "latest_water_date",
    # These fields drive the CAM Trees table column and Nuts Present map theme.
    "nuts_present",
    "latest_nuts_date",
    "longitude",
    "latitude",
    "elevation_in_feet",
    "access_path",
    "access_level",
    "access_method",
    "access_note",
    "form",
    "planting_method",
    "wire_fence",
    "mother_tree",
    "mother_tree_other",
    "father_tree",
    "father_tree_other",
    "parent_tree_note",
    "note",
)

CAM_SITE_COLUMNS = (
    "site",
    "org_code",
    "organization",
    "site_url",
    "town",
    "site_location",
    "location_note",
    "contact",
    "primary_caretaker",
    "secondary_caretaker",
    "longitude",
    "latitude",
)

CAM_ORG_COLUMNS = (
    "org_code",
    "organization",
    "contact",
)

CAM_HUB_COLUMNS = (
    "hub",
    "captain",
    "lieutenant",
)

SITE_VISIT_COLUMNS = (
    "Site",
    "Tree ID",
    "Date Planted",
    "Health",
    "Access Path",
    "Access Level",
    "GPS Locked",
    "Planting Method",
    "Wire Fence",
    "Mother Tree",
    "Father Tree",
    "Parent Tree Note",
    "Note",
)

PARENT_TREE_COLUMNS = (
    "parent_tree",
)

# Public Sites in Hubs rows contain one site-to-hub association per record.
SITES_HUBS_COLUMNS = (
    "site",
    "hub",
)

# View and output are deliberately hard-coded.  Do not put credentials in a
# site configuration file or client-side JavaScript.
EXPORTS = (
    {
        "name": "cam_trees",
        "view": "public_cam_trees",
        "columns": CAM_TREE_COLUMNS,
        "output": ROOT / "data" / "cam_trees.json",
        "order_by": '"site", "tree_id", "cam_org", "hub"',
    },
    {
        "name": "cam_sites",
        "view": "public_cam_sites",
        "columns": CAM_SITE_COLUMNS,
        "output": ROOT / "data" / "cam_sites.json",
        "order_by": '"org_code", "site"',
    },
    {
        "name": "cam_orgs",
        "view": "public_cam_orgs",
        "columns": CAM_ORG_COLUMNS,
        "output": ROOT / "data" / "cam_orgs.json",
        "order_by": '"organization"',
    },
    {
        "name": "cam_hubs",
        "view": "public_cam_hubs",
        "columns": CAM_HUB_COLUMNS,
        "output": ROOT / "data" / "cam_hubs.json",
        "order_by": '"hub"',
    },
    {
        "name": "site_visit",
        "view": "public_site_visit",
        "columns": SITE_VISIT_COLUMNS,
        "output": ROOT / "data" / "site_visit.json",
        "order_by": '"Site", "Tree ID"',
    },
    {
        "name": "parent_trees",
        "view": "public_parent_trees",
        "columns": PARENT_TREE_COLUMNS,
        "output": ROOT / "data" / "parent_trees.json",
        "order_by": '"parent_tree"',
    },
    {
        # Keep this public view name synchronized with the database definition.
        "name": "sites_hubs",
        "view": "public_sites_hubs",
        "columns": SITES_HUBS_COLUMNS,
        "output": ROOT / "data" / "sites_hubs.json",
        "order_by": '"site", "hub"',
    },
)


def json_default(value: Any) -> str | float:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def export_data(database_url: str, export: dict[str, Any]) -> None:
    columns = export["columns"]
    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    query = (
        f"SELECT {quoted_columns} FROM {export['view']} "
        f"ORDER BY {export['order_by']}"
    )

    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            records = [dict(row) for row in cursor.fetchall()]

    payload = {"records": records}
    output = Path(export["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(".json.tmp")
    temporary_output.write_text(
        json.dumps(payload, default=json_default, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_output.replace(output)
    print(f"Exported {len(records)} records to {output.relative_to(ROOT)}")


def main() -> None:
    database_url = os.environ.get("NEON_DATABASE_URL")
    if not database_url:
        raise SystemExit("NEON_DATABASE_URL is required (configure it as a GitHub Actions secret).")

    for export in EXPORTS:
        export_data(database_url, export)


if __name__ == "__main__":
    main()
