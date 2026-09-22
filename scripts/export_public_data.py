#!/usr/bin/env python3
"""Export approved database views to static JSON files.

Add a new entry to EXPORTS when another view is ready. Protected columns must
be listed in encrypted_columns so their plaintext never reaches the JSON file.
Keeping the allow-list here avoids accepting arbitrary table names from input.
"""

from __future__ import annotations

import json
import os
import base64
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parents[1]
KEY_DERIVATION_ITERATIONS = 310_000

CAM_TREE_COLUMNS = (
    "site",
    "tree_id",
    "town",
    "hub",
    "cam_org",
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
    "latitude",
    "longitude",
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
    "town",
    "hub",
    "org_code",
    "organization",
    "site_url",
    "site_location",
    "location_note",
    "contact",
    "primary_caretaker",
    "secondary_caretaker",
    "latitude",
    "longitude",
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
    # Hub coordinates support the filtered CAM Hubs map.
    "latitude",
    "longitude",
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
        "order_by": '"site", "tree_id"',
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
    {
        # Add future protected exports here and list every column requiring
        # encryption. The corresponding table configuration marks them encrypted.
        "name": "test_data",
        "view": "public_test_data",
        "columns": ("user_name", "phone_number"),
        "encrypted_columns": ("phone_number",),
        "encryption_key_env": "CHESTNUT_CHASERS_DECRYPTION_KEY",
        "output": ROOT / "data" / "test_data.json",
        "order_by": '"user_name"',
    },
)


def json_default(value: Any) -> str | float:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def encrypt_records(records: list[dict[str, Any]], export: dict[str, Any], secret: str) -> dict[str, Any]:
    """Replace designated values with authenticated ciphertext before JSON is written."""
    encrypted_columns = tuple(export["encrypted_columns"])
    if not encrypted_columns or not set(encrypted_columns).issubset(export["columns"]):
        raise ValueError(f"Invalid encrypted_columns configuration for {export['name']}")

    salt = os.urandom(16)
    key = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt,
                    iterations=KEY_DERIVATION_ITERATIONS).derive(secret.encode("utf-8"))
    cipher = AESGCM(key)
    for index, row in enumerate(records):
        for column in encrypted_columns:
            value = row[column]
            if value is None:
                continue
            nonce = os.urandom(12)
            # Bind ciphertext to its intended column and row position.
            context = f"{export['name']}:{column}:{index}".encode("utf-8")
            ciphertext = cipher.encrypt(nonce, str(value).encode("utf-8"), context)
            row[column] = {
                "nonce": base64.b64encode(nonce).decode("ascii"),
                "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            }
    # This authenticated check proves the key is correct even for an empty
    # export or an export whose protected values are all NULL.
    check_nonce = os.urandom(12)
    check_ciphertext = cipher.encrypt(check_nonce, b"cam-data-unlock-v1", export["name"].encode("utf-8"))
    return {
        "version": 1,
        "algorithm": "AES-256-GCM",
        "kdf": "PBKDF2-SHA-256",
        "iterations": KEY_DERIVATION_ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "columns": list(encrypted_columns),
        "context": export["name"],
        "check": {
            "nonce": base64.b64encode(check_nonce).decode("ascii"),
            "ciphertext": base64.b64encode(check_ciphertext).decode("ascii"),
        },
    }


def export_data(database_url: str, export: dict[str, Any]) -> None:
    # Fail before querying or writing if an encrypted export has no secret.
    secret = os.environ.get(export.get("encryption_key_env", "")) if export.get("encrypted_columns") else None
    if export.get("encrypted_columns") and not secret:
        raise RuntimeError(f"Missing encryption secret for {export['name']}")
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
    if secret:
        payload["encryption"] = encrypt_records(records, export, secret)
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
    database_url = os.environ.get("CAMTREES_READ_URL")
    if not database_url:
        raise SystemExit("CAMTREES_READ_URL is required (configure it as a GitHub Actions secret).")

    for export in EXPORTS:
        export_data(database_url, export)


if __name__ == "__main__":
    main()
