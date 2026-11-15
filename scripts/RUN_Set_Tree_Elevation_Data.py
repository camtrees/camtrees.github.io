##########################################################################################
## Program  : RUN_Set_Tree_Elevation_Data.py
##
## Purpose  : Update elevation_in_feet for trees with a NULL value.
##
## Note     : Gets SRTM elevation data through the pyhigh Python package.
##
## Requires : pyhigh Python Package
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-03-05 Initial Version
##            2026-06-11 Now using Neon CAMorg 'camtrees' database as the master
##            2026-07-09 Use .env file to load database connection parameters
##            2026-07-20 Add capability to use either the Neon CAMTREES master
##                       database or the KENSTER backup database
##            2026-07-22 Changes for using config.py file
##            2026-09-04 Changes for using updated config.py and .env files
##            2026-09-04 Using psycopg (version 3) vs psycopg2
##            2026-11-14 Add batch lookup, validation, and failure reporting
##########################################################################################

from dataclasses import dataclass
import math

import psycopg
from pyhigh import get_elevation, get_elevation_batch

# Load the writable database URL selected by config.py.
from config import DB_HOST_WRITE


METERS_TO_FEET = 3.280839895

# SRTM elevation files use -32768 to indicate a location with no elevation data.
SRTM_VOID_ELEVATION_METERS = -32768


@dataclass(frozen=True)
class TreeElevationCandidate:
    """A tree whose coordinates may be used to fill its missing elevation."""

    tree_id: int
    site_id: int
    tag_id: str
    longitude: object
    latitude: object


def get_trees_with_missing_elevations(cursor):
    """Return trees that have coordinates but do not yet have an elevation."""
    cursor.execute(
        "SELECT id, site_id, tag_id, longitude, latitude "
        "FROM tree "
        "WHERE elevation_in_feet IS NULL "
        "AND longitude IS NOT NULL "
        "AND latitude IS NOT NULL "
        "ORDER BY id;"
    )
    return [TreeElevationCandidate(*row) for row in cursor.fetchall()]


def validated_coordinates(tree):
    """Return latitude and longitude as floats, or None when they are invalid."""
    try:
        latitude = float(tree.latitude)
        longitude = float(tree.longitude)
    except (TypeError, ValueError, OverflowError):
        return None

    if not math.isfinite(latitude) or not math.isfinite(longitude):
        return None
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return None

    return latitude, longitude


def valid_elevation(elevation):
    """Return a finite elevation, allowing legitimate values below sea level."""
    try:
        elevation = float(elevation)
    except (TypeError, ValueError, OverflowError):
        return None

    if not math.isfinite(elevation):
        return None
    if elevation == SRTM_VOID_ELEVATION_METERS:
        return None

    return elevation


def lookup_elevations(trees):
    """Look up elevations in a batch, with individual retries after batch failure."""
    valid_trees = []
    invalid_trees = []

    for tree in trees:
        coordinates = validated_coordinates(tree)
        if coordinates is None:
            invalid_trees.append(tree)
            print(
                "Invalid coordinates for database tree ID "
                f"{tree.tree_id} (Site ID: {tree.site_id}, Tag ID: {tree.tag_id}, "
                f"Longitude: {tree.longitude}, Latitude: {tree.latitude})."
            )
            continue
        valid_trees.append((tree, coordinates))

    elevations = {}
    lookup_failures = []
    coordinate_list = [coordinates for _, coordinates in valid_trees]

    if coordinate_list:
        try:
            batch_results = get_elevation_batch(coordinate_list)
            if len(batch_results) != len(valid_trees):
                raise RuntimeError(
                    "The elevation service returned an unexpected number of results."
                )

            for (tree, _), result in zip(valid_trees, batch_results):
                elevation = valid_elevation(result)
                if elevation is None:
                    lookup_failures.append(tree)
                    print(
                        "No valid elevation was returned for database tree ID "
                        f"{tree.tree_id} (Tag ID: {tree.tag_id})."
                    )
                else:
                    elevations[tree.tree_id] = elevation
        except Exception as batch_error:
            # A single unavailable or corrupt SRTM tile can make a batch fail.
            # Retry one tree at a time so trees in other tiles can still update.
            print(
                "The batch elevation lookup failed; retrying each tree separately. "
                f"Reason: {batch_error}"
            )
            for tree, (latitude, longitude) in valid_trees:
                try:
                    elevation = valid_elevation(
                        get_elevation(lat=latitude, lon=longitude)
                    )
                    if elevation is None:
                        raise ValueError("No valid elevation was returned.")
                    elevations[tree.tree_id] = elevation
                except Exception as lookup_error:
                    lookup_failures.append(tree)
                    print(
                        "Elevation lookup failed for database tree ID "
                        f"{tree.tree_id} (Tag ID: {tree.tag_id}). "
                        f"Reason: {lookup_error}"
                    )

    return elevations, invalid_trees, lookup_failures


def update_tree_elevations(cursor, trees, elevations):
    """Store retrieved elevations without overwriting concurrent changes."""
    trees_updated = 0
    concurrently_skipped = 0
    database_failures = []

    for tree in trees:
        elevation_meters = elevations.get(tree.tree_id)
        if elevation_meters is None:
            continue

        elevation_feet = elevation_meters * METERS_TO_FEET
        try:
            cursor.execute(
                "UPDATE tree "
                "SET elevation_in_feet = %s "
                "WHERE id = %s AND elevation_in_feet IS NULL;",
                (elevation_feet, tree.tree_id),
            )
        except psycopg.Error as database_error:
            database_failures.append(tree)
            print(
                "Database update failed for database tree ID "
                f"{tree.tree_id} (Tag ID: {tree.tag_id}). "
                f"Reason: {database_error}"
            )
            continue

        if cursor.rowcount == 1:
            trees_updated += 1
            print(
                f"Updated database tree ID: {tree.tree_id} "
                f"(Site ID: {tree.site_id}, Tag ID: {tree.tag_id}, "
                f"Longitude: {tree.longitude}, Latitude: {tree.latitude}) "
                f"with Elevation: {elevation_feet} Feet"
            )
        else:
            # Another process may have supplied the elevation after our SELECT.
            concurrently_skipped += 1
            print(
                "Skipped database tree ID "
                f"{tree.tree_id} because its elevation is no longer NULL."
            )

    return trees_updated, concurrently_skipped, database_failures


def main():
    if not DB_HOST_WRITE:
        raise RuntimeError(
            "A writable database URL is required. Configure CAMTREES_WRITE_URL "
            "or KENSTER_WRITE_URL for the database selected in config.py."
        )

    # Autocommit preserves each successful update even if a later tree fails.
    with psycopg.connect(DB_HOST_WRITE, autocommit=True) as connection:
        with connection.cursor() as cursor:
            trees = get_trees_with_missing_elevations(cursor)

            if not trees:
                print(
                    "\n######################################################################"
                    "\n## No trees found with NULL elevation and GPS coordinates provided. ##"
                    "\n######################################################################"
                )
                return

            print(
                "\n###########################################################################"
                f"\n## Found {len(trees)} trees with NULL elevation and GPS coordinates provided. ##"
                "\n###########################################################################"
            )

            elevations, invalid_trees, lookup_failures = lookup_elevations(trees)
            updated, concurrent_skips, database_failures = update_tree_elevations(
                cursor, trees, elevations
            )

    total_failures = (
        len(invalid_trees) + len(lookup_failures) + len(database_failures)
    )
    print(
        "\nElevation maintenance summary:"
        f"\n  Trees selected:             {len(trees)}"
        f"\n  Trees updated:              {updated}"
        f"\n  Invalid coordinates:        {len(invalid_trees)}"
        f"\n  Elevation lookup failures:  {len(lookup_failures)}"
        f"\n  Database update failures:   {len(database_failures)}"
        f"\n  Concurrent updates skipped: {concurrent_skips}"
    )

    # Make the GitHub Actions step visibly fail while retaining successful rows.
    if total_failures:
        raise RuntimeError(
            f"Elevation maintenance completed with {total_failures} failure(s)."
        )


if __name__ == "__main__":
    main()
