#!/usr/bin/env python3
"""Adjust shared Hub boundaries around specifically assigned CAM sites.

The input GeoJSON stores polygon rings as outline-only LineStrings for
Leaflet. This script reconstructs the polygons, gives each named site a
300-metre clearance inside its assigned Hub, and writes the polygons back as
outlines. Claimed land is removed from every other Hub at the same time, so
the complete coverage remains gap-free and non-overlapping.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import nearest_points, transform, unary_union


CLEARANCE_METRES = 300
SITE_ASSIGNMENTS = {
    "Campus": "Sanford",
    "Dead River Trailhead Log Landing": "Ellsworth",
    "Dead River Trailhead Capstone Trail": "Ellsworth",
    "Erickson Fields Preserve": "Searsport",
    "Hebron Station School": "Bridgton",
    "Shepard’s Farm Preserve": "Bethel",
}


def polygon_parts(geometry):
    """Return only polygon components from a possibly mixed geometry."""
    if isinstance(geometry, Polygon):
        return [geometry]
    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)
    return [part for part in geometry.geoms if isinstance(part, Polygon)]


def boundary_to_polygon(feature, project):
    """Reconstruct one Hub polygon from its closed Leaflet outline rings."""
    geometry = feature["geometry"]
    rings = [geometry["coordinates"]] if geometry["type"] == "LineString" else geometry["coordinates"]
    polygons = []
    for ring in rings:
        polygon = transform(project, Polygon(ring))
        polygons.extend(polygon_parts(polygon if polygon.is_valid else polygon.buffer(0)))
    return unary_union(polygons)


def rounded_ring(ring, unproject):
    """Return a closed polygon ring as two-dimensional longitude/latitude."""
    return [
        [round(longitude, 10), round(latitude, 10)]
        for longitude, latitude in (unproject(x, y) for x, y in ring.coords)
    ]


def polygon_to_boundary(geometry, unproject):
    """Convert polygons back to the outline-only contract used by Leaflet."""
    rings = []
    for polygon in polygon_parts(geometry):
        rings.append(rounded_ring(polygon.exterior, unproject))
        rings.extend(rounded_ring(interior, unproject) for interior in polygon.interiors)
    if len(rings) == 1:
        return {"type": "LineString", "coordinates": rings[0]}
    return {"type": "MultiLineString", "coordinates": rings}


def interior_center(geometry):
    """Choose a central point that is guaranteed to remain inside its Hub."""
    component = max(polygon_parts(geometry), key=lambda part: part.area)
    center = component.centroid
    return center if component.covers(center) else component.representative_point()


def load_records(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    return payload.get("records", payload.get("data", []))


def validate(areas, original_domain, assigned_points):
    """Verify topology and ensure every corrected site has visible clearance."""
    combined = unary_union(list(areas.values()))
    tolerance = 1.0  # Square metres, allowing harmless floating-point noise.
    overlap = sum(area.area for area in areas.values()) - combined.area
    uncovered = original_domain.difference(combined).area
    outside = combined.difference(original_domain).area
    if max(overlap, uncovered, outside) > tolerance:
        raise ValueError(
            f"Topology failed: overlap={overlap:.3f}, uncovered={uncovered:.3f}, outside={outside:.3f}"
        )

    for site_name, hub_name, point in assigned_points:
        if not areas[hub_name].covers(point):
            raise ValueError(f"{site_name} is not inside {hub_name}")
        clearance = areas[hub_name].boundary.distance(point)
        # Exterior coastline can limit clearance, although none of the named
        # corrections is expected to encounter that special case.
        if clearance < CLEARANCE_METRES - 1:
            raise ValueError(f"{site_name} has only {clearance:.1f} m of boundary clearance")


def adjust(geojson_path, sites_path, output_path):
    source_text = geojson_path.read_text(encoding="utf-8")
    payload = json.loads(source_text)
    sites = {record.get("site"): record for record in load_records(sites_path)}
    assignment_metadata = []
    for site_name, hub_name in SITE_ASSIGNMENTS.items():
        record = sites.get(site_name)
        if not record or record.get("longitude") is None or record.get("latitude") is None:
            raise ValueError(f"Missing coordinates for site: {site_name}")
        assignment_metadata.append({
            "site": site_name,
            "hub": hub_name,
            "longitude": float(record["longitude"]),
            "latitude": float(record["latitude"]),
        })

    # Avoid repeatedly reprocessing already adjusted curves. A future change to
    # a named site's assignment or coordinates automatically bypasses this.
    metadata = payload.get("metadata", {})
    if (
        metadata.get("boundary_adjustment_sites") == assignment_metadata
        and metadata.get("boundary_adjustment_clearance_metres") == CLEARANCE_METRES
    ):
        output_path.write_text(source_text, encoding="utf-8")
        print(f"No adjustment needed; {output_path} already contains the current assignments")
        return

    project = Transformer.from_crs(4326, 5070, always_xy=True)
    unproject = Transformer.from_crs(5070, 4326, always_xy=True)

    boundary_features = {
        feature["properties"]["Name"]: feature
        for feature in payload["features"]
        if feature["properties"].get("feature_type") == "boundary"
    }
    areas = {
        name: boundary_to_polygon(feature, project.transform)
        for name, feature in boundary_features.items()
    }
    original_domain = unary_union(list(areas.values()))

    assigned_points = []
    for assignment in assignment_metadata:
        site_name = assignment["site"]
        hub_name = assignment["hub"]
        record = sites[site_name]
        point = Point(*project.transform(float(record["longitude"]), float(record["latitude"])))
        assigned_points.append((site_name, hub_name, point))

        # A round site buffer provides discernible separation from the final
        # boundary. When necessary, a narrow rounded corridor connects that
        # buffer to the assigned Hub instead of creating a detached island.
        claimed = point.buffer(CLEARANCE_METRES)
        if not areas[hub_name].covers(point):
            destination = nearest_points(point, areas[hub_name])[1]
            claimed = unary_union([
                claimed,
                LineString([point, destination]).buffer(CLEARANCE_METRES),
            ])
        claimed = claimed.intersection(original_domain)
        areas[hub_name] = unary_union([areas[hub_name], claimed])
        for other_name in areas:
            if other_name != hub_name:
                areas[other_name] = areas[other_name].difference(claimed)

    validate(areas, original_domain, assigned_points)

    # Replace all boundary geometries so both sides of every changed edge use
    # exactly the same curve or line, then recenter the corresponding labels.
    for name, feature in boundary_features.items():
        feature["geometry"] = polygon_to_boundary(areas[name], unproject.transform)
    for feature in payload["features"]:
        if feature["properties"].get("feature_type") != "center":
            continue
        name = feature["properties"]["Name"]
        center = transform(unproject.transform, interior_center(areas[name]))
        feature["geometry"] = {
            "type": "Point",
            "coordinates": [round(center.x, 10), round(center.y, 10)],
        }
        feature["properties"]["center_method"] = "adjusted_polygon_centroid_or_interior_point"

    metadata = payload.setdefault("metadata", {})
    history = metadata.setdefault("processing_history", [])
    note = (
        "Adjusted shared Hub boundaries using CAM Sites coordinates so Campus is in Sanford; "
        "both Dead River Trailhead sites are in Ellsworth; Erickson Fields Preserve is in "
        "Searsport; Hebron Station School is in Bridgton; and Shepard’s Farm Preserve is in "
        f"Bethel. Each site has at least {CLEARANCE_METRES} metres of clearance."
    )
    if note not in history:
        history.append(note)
    metadata["boundary_adjustment_source"] = sites_path.name
    metadata["boundary_adjustment_script"] = "scripts/adjust_hub_boundaries_for_sites.py"
    metadata["boundary_adjustment_clearance_metres"] = CLEARANCE_METRES
    metadata["boundary_adjustment_sites"] = assignment_metadata
    metadata["topology_after_adjustment"] = "Complete original coverage with no intentional gaps or overlaps."

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {output_path} for {len(assigned_points)} assigned sites")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geojson", type=Path, default=Path("data/hub-areas.geojson"))
    parser.add_argument("--sites", type=Path, default=Path("data/cam_sites.json"))
    parser.add_argument("--output", type=Path, default=Path("data/hub-areas.geojson"))
    arguments = parser.parse_args()
    adjust(arguments.geojson, arguments.sites, arguments.output)


if __name__ == "__main__":
    main()
