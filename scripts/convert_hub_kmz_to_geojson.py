#!/usr/bin/env python3
"""Convert the revised Hub KMZ into the GeoJSON contract used by Leaflet.

Area polygons become outline-only boundary features so the existing Leaflet
overlay continues to draw green lines rather than polygon fills. Hub points
become center features used for black triangle markers and permanent labels.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET


KML_NAMESPACE = "http://www.opengis.net/kml/2.2"
NS = {"k": KML_NAMESPACE}
AREA_FOLDER = "ME Hub Areas_3-17-26"
CENTER_FOLDER = "ME Hub Centers - 3-17-26"


def folder_named(root: ET.Element, name: str) -> ET.Element:
    for folder in root.findall(".//k:Folder", NS):
        if folder.findtext("k:name", default="", namespaces=NS) == name:
            return folder
    raise ValueError(f"KML folder not found: {name}")


def coordinates(node: ET.Element) -> list[list[float]]:
    text = node.findtext("k:coordinates", default="", namespaces=NS)
    return [
        [float(values[0]), float(values[1])]
        for item in text.split()
        if len(values := item.split(",")) >= 2
    ]


def boundary_geometry(placemark: ET.Element) -> dict:
    """Return every polygon ring as an outline geometry for Leaflet."""
    rings: list[list[list[float]]] = []
    for polygon in placemark.findall(".//k:Polygon", NS):
        outer = polygon.find("k:outerBoundaryIs/k:LinearRing", NS)
        if outer is not None:
            rings.append(coordinates(outer))
        for inner in polygon.findall("k:innerBoundaryIs/k:LinearRing", NS):
            rings.append(coordinates(inner))
    if not rings:
        raise ValueError(f"Area has no Polygon rings: {placemark_name(placemark)}")
    if len(rings) == 1:
        return {"type": "LineString", "coordinates": rings[0]}
    return {"type": "MultiLineString", "coordinates": rings}


def placemark_name(placemark: ET.Element) -> str:
    return placemark.findtext("k:name", default="", namespaces=NS)


def placemark_description(placemark: ET.Element) -> str:
    return placemark.findtext("k:description", default="", namespaces=NS)


def convert(source: Path, destination: Path) -> None:
    with ZipFile(source) as archive:
        root = ET.fromstring(archive.read("doc.kml"))

    area_folder = folder_named(root, AREA_FOLDER)
    center_folder = folder_named(root, CENTER_FOLDER)
    features: list[dict] = []

    for placemark in area_folder.findall("k:Placemark", NS):
        name = placemark_name(placemark)
        properties: dict = {
            "Name": name,
            "Description": placemark_description(placemark),
            "feature_type": "boundary",
        }
        if name == "Warren":
            properties["union_members"] = ["Warren", "+Warren"]
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": boundary_geometry(placemark),
            }
        )

    for placemark in center_folder.findall("k:Placemark", NS):
        name = placemark_name(placemark)
        point = placemark.find(".//k:Point", NS)
        if point is None:
            raise ValueError(f"Hub center has no Point: {name}")
        point_coordinates = coordinates(point)
        if len(point_coordinates) != 1:
            raise ValueError(f"Hub center does not contain exactly one coordinate: {name}")
        properties = {
            "Name": name,
            "Description": placemark_description(placemark),
            "feature_type": "center",
            "center_method": "final_polygon_centroid_or_interior_point",
        }
        if name == "Warren":
            properties["union_members"] = ["Warren", "+Warren"]
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {"type": "Point", "coordinates": point_coordinates[0]},
            }
        )

    boundary_names = {
        feature["properties"]["Name"]
        for feature in features
        if feature["properties"]["feature_type"] == "boundary"
    }
    center_names = {
        feature["properties"]["Name"]
        for feature in features
        if feature["properties"]["feature_type"] == "center"
    }
    if boundary_names != center_names:
        raise ValueError(
            f"Boundary and center names differ: boundaries={sorted(boundary_names)}, centers={sorted(center_names)}"
        )

    payload = {
        "type": "FeatureCollection",
        "metadata": {
            "purpose": "One public Leaflet overlay containing CAM Hub boundaries, centers, and Hub names.",
            "source_file": source.name,
            "processing_history": [
                "Converted the revised KMZ polygons and center points to RFC 7946 GeoJSON.",
                "Exported polygon rings as outline-only boundary LineStrings or MultiLineStrings for Leaflet.",
                "Removed unused altitude coordinates so all coordinates are two-dimensional longitude and latitude.",
                "Retained the merged Warren area and its single repositioned center.",
                "Excluded the Coastal Downeast no-grow zone, which is absent from the revised KMZ.",
            ],
            "current_contents": f"{len(boundary_names)} Hub boundary features and {len(center_names)} corresponding center Points.",
            "feature_properties": {
                "Name": "The Hub name displayed by the Leaflet overlay.",
                "Description": "Description retained from the source KMZ when present.",
                "feature_type": "Either boundary or center.",
                "center_method": "For center features, identifies how the center was selected.",
                "union_members": "For Warren, records the two original area names.",
            },
            "display_behavior": "Leaflet renders boundaries as green lines and centers as black triangles with permanent Hub-name labels.",
            "maintenance_note": "This metadata object is a valid GeoJSON foreign member that Leaflet safely ignores.",
        },
        "features": features,
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {destination} with {len(features)} features")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    convert(arguments.source, arguments.destination)


if __name__ == "__main__":
    main()
