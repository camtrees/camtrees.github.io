#!/usr/bin/env python3
"""Build adjoining, non-overlapping Hub polygons from a Google Earth KMZ.

The input's circle-like outlines are converted to polygons and fitted to
circles in an equal-area projection. A power-diagram partition uses the
circles' common chords as shared boundaries. Enclosed holes in the combined
outside boundary are assigned to the nearest weighted Hub region.

The Coastal Downeast no-grow zone is omitted from both the output and the
coverage boundary. Warren and +Warren participate as separate circle
generators, then their assigned pieces are dissolved into one Warren polygon
without an internal boundary. Existing Hub-center points are moved to interior
polygon centers.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET

import numpy as np
from pyproj import Transformer
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import transform, unary_union


KML = "http://www.opengis.net/kml/2.2"
GX = "http://www.google.com/kml/ext/2.2"
ATOM = "http://www.w3.org/2005/Atom"
NS = {"k": KML}
AREA_FOLDER = "ME Hub Areas_3-17-26"
CENTER_FOLDER = "ME Hub Centers - 3-17-26"
COASTAL = "Coastal Downeast - No-Grow Zone"


def tag(name: str) -> str:
    return f"{{{KML}}}{name}"


def folder_named(root: ET.Element, name: str) -> ET.Element:
    for folder in root.findall(".//k:Folder", NS):
        if folder.findtext("k:name", default="", namespaces=NS) == name:
            return folder
    raise ValueError(f"KML folder not found: {name}")


def placemark_name(placemark: ET.Element) -> str:
    return placemark.findtext("k:name", default="", namespaces=NS)


def read_outline(placemark: ET.Element, project) -> Polygon:
    text = placemark.findtext(".//k:LineString/k:coordinates", default="", namespaces=NS)
    if not text:
        raise ValueError(f"Area has no LineString coordinates: {placemark_name(placemark)}")
    coordinates = [tuple(map(float, value.split(",")[:2])) for value in text.split()]
    geometry = transform(project, Polygon(coordinates))
    return geometry if geometry.is_valid else geometry.buffer(0)


def fitted_circle(polygon: Polygon) -> tuple[float, float, float]:
    """Fit a circle to the outline with a least-squares algebraic solution."""
    points = np.asarray(polygon.exterior.coords[:-1])
    x_values, y_values = points[:, 0], points[:, 1]
    matrix = np.column_stack((2 * x_values, 2 * y_values, np.ones(len(points))))
    right_side = x_values**2 + y_values**2
    center_x, center_y, constant = np.linalg.lstsq(matrix, right_side, rcond=None)[0]
    radius = float(np.sqrt(constant + center_x**2 + center_y**2))
    return float(center_x), float(center_y), radius


def half_plane(bounds: tuple[float, float, float, float], a: float, b: float, d: float) -> Polygon:
    """Return a large polygon representing the linear inequality ax+by <= d."""
    min_x, min_y, max_x, max_y = bounds
    pad = max(max_x - min_x, max_y - min_y) * 3
    square = [
        (min_x - pad, min_y - pad),
        (max_x + pad, min_y - pad),
        (max_x + pad, max_y + pad),
        (min_x - pad, max_y + pad),
    ]
    output: list[tuple[float, float]] = []
    for start, end in zip(square, square[1:] + square[:1]):
        start_value = a * start[0] + b * start[1] - d
        end_value = a * end[0] + b * end[1] - d
        start_inside = start_value <= 1e-7
        end_inside = end_value <= 1e-7
        if start_inside:
            output.append(start)
        if start_inside != end_inside:
            fraction = start_value / (start_value - end_value)
            output.append(
                (
                    start[0] + fraction * (end[0] - start[0]),
                    start[1] + fraction * (end[1] - start[1]),
                )
            )
    return Polygon(output) if len(output) >= 3 else Polygon()


def filled_exterior(geometries: list[Polygon]):
    """Preserve natural exterior components while filling enclosed holes."""
    combined = unary_union(geometries)
    components = list(combined.geoms) if isinstance(combined, MultiPolygon) else [combined]
    return unary_union([Polygon(component.exterior) for component in components])


def build_partition(outlines: dict[str, Polygon]) -> tuple[dict[str, Polygon], object]:
    # The no-grow zone is intentionally ignored when determining both the
    # combined outside boundary and the final list of areas.
    hub_outlines = {name: outline for name, outline in outlines.items() if name != COASTAL}
    domain = filled_exterior(list(hub_outlines.values()))

    generators = []
    for name, outline in hub_outlines.items():
        generators.append((name, *fitted_circle(outline)))

    allocated: dict[str, Polygon] = {}
    for index, (name, center_x, center_y, radius) in enumerate(generators):
        cell = domain
        for other_index, (_, other_x, other_y, other_radius) in enumerate(generators):
            if index == other_index:
                continue
            # Comparing the two circles' power distances produces their
            # common chord (radical axis) as the shared straight boundary.
            a = 2 * (other_x - center_x)
            b = 2 * (other_y - center_y)
            d = (
                other_x**2 + other_y**2 - other_radius**2
                - center_x**2 - center_y**2 + radius**2
            )
            cell = cell.intersection(half_plane(domain.bounds, a, b, d))
            if cell.is_empty:
                break
        final_name = "Warren" if name in {"Warren", "+Warren"} else name
        allocated[final_name] = unary_union([allocated[final_name], cell]) if final_name in allocated else cell

    return allocated, domain


def polygon_parts(geometry) -> list[Polygon]:
    if isinstance(geometry, Polygon):
        return [geometry]
    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)
    return [part for part in geometry.geoms if isinstance(part, Polygon)]


def coordinate_text(ring, unproject) -> str:
    return " ".join(
        f"{longitude:.10f},{latitude:.10f},0"
        for longitude, latitude in (unproject(x_value, y_value) for x_value, y_value in ring.coords)
    )


def polygon_element(polygon: Polygon, unproject) -> ET.Element:
    element = ET.Element(tag("Polygon"))
    ET.SubElement(element, tag("tessellate")).text = "1"
    ET.SubElement(element, tag("altitudeMode")).text = "clampToGround"
    outer = ET.SubElement(element, tag("outerBoundaryIs"))
    outer_ring = ET.SubElement(outer, tag("LinearRing"))
    ET.SubElement(outer_ring, tag("coordinates")).text = coordinate_text(polygon.exterior, unproject)
    for interior in polygon.interiors:
        inner = ET.SubElement(element, tag("innerBoundaryIs"))
        inner_ring = ET.SubElement(inner, tag("LinearRing"))
        ET.SubElement(inner_ring, tag("coordinates")).text = coordinate_text(interior, unproject)
    return element


def replace_area_geometry(placemark: ET.Element, geometry, unproject) -> None:
    for child in list(placemark):
        if child.tag in {tag("LineString"), tag("Polygon"), tag("MultiGeometry")}:
            placemark.remove(child)

    parts = polygon_parts(geometry)
    if len(parts) == 1:
        placemark.append(polygon_element(parts[0], unproject))
    else:
        multi = ET.SubElement(placemark, tag("MultiGeometry"))
        for part in parts:
            multi.append(polygon_element(part, unproject))

    # Original areas were outline-only LineStrings. Keep them visually
    # outline-only after changing their geometry type to Polygon.
    inline_style = placemark.find("k:Style", NS)
    if inline_style is None:
        inline_style = ET.Element(tag("Style"))
        geometry_index = next(
            (index for index, child in enumerate(placemark) if child.tag in {tag("Polygon"), tag("MultiGeometry")}),
            len(placemark),
        )
        placemark.insert(geometry_index, inline_style)
    poly_style = inline_style.find("k:PolyStyle", NS)
    if poly_style is None:
        poly_style = ET.SubElement(inline_style, tag("PolyStyle"))
    fill = poly_style.find("k:fill", NS) or ET.SubElement(poly_style, tag("fill"))
    outline = poly_style.find("k:outline", NS) or ET.SubElement(poly_style, tag("outline"))
    fill.text, outline.text = "0", "1"


def interior_center(geometry) -> tuple[float, float]:
    """Prefer the centroid, falling back to a guaranteed interior point."""
    parts = polygon_parts(geometry)
    component = max(parts, key=lambda part: part.area)
    center = component.centroid
    if not component.covers(center):
        center = component.representative_point()
    return center.x, center.y


def validate(areas: dict[str, Polygon], domain, centers: dict[str, tuple[float, float]]) -> None:
    combined = unary_union(list(areas.values()))
    tolerance = 0.1  # square metres; accommodates floating-point overlay noise.
    uncovered = domain.difference(combined).area
    outside = combined.difference(domain).area
    overlap = sum(area.area for area in areas.values()) - combined.area
    if uncovered > tolerance or outside > tolerance or overlap > tolerance:
        raise ValueError(
            f"Topology validation failed: uncovered={uncovered}, outside={outside}, overlap={overlap}"
        )
    for name, center in centers.items():
        from shapely.geometry import Point

        if name not in areas or not areas[name].covers(Point(center)):
            raise ValueError(f"Hub center is not inside its final area: {name}")


def rebuild(source: Path, destination: Path) -> None:
    project = Transformer.from_crs(4326, 5070, always_xy=True)
    unproject = Transformer.from_crs(5070, 4326, always_xy=True)

    with ZipFile(source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    root = ET.fromstring(members["doc.kml"])
    area_folder = folder_named(root, AREA_FOLDER)
    center_folder = folder_named(root, CENTER_FOLDER)

    area_placemarks = {placemark_name(pm): pm for pm in area_folder.findall("k:Placemark", NS)}
    outlines = {
        name: read_outline(placemark, project.transform)
        for name, placemark in area_placemarks.items()
    }
    areas, domain = build_partition(outlines)

    # Reuse Warren's styling and position. Remove both the obsolete +Warren
    # feature and the intentionally excluded Coastal Downeast no-grow zone.
    plus_warren = area_placemarks.get("+Warren")
    if plus_warren is not None:
        area_folder.remove(plus_warren)
    coastal = area_placemarks.get(COASTAL)
    if coastal is not None:
        area_folder.remove(coastal)
    for name, geometry in areas.items():
        replace_area_geometry(area_placemarks[name], geometry, unproject.transform)

    centers: dict[str, tuple[float, float]] = {}
    for placemark in center_folder.findall("k:Placemark", NS):
        name = placemark_name(placemark)
        if name not in areas:
            continue
        center = interior_center(areas[name])
        centers[name] = center
        coordinate_node = placemark.find(".//k:Point/k:coordinates", NS)
        if coordinate_node is None:
            raise ValueError(f"Hub center has no Point coordinates: {name}")
        longitude, latitude = unproject.transform(*center)
        coordinate_node.text = f"{longitude:.10f},{latitude:.10f},0"

    validate(areas, domain, centers)

    ET.register_namespace("", KML)
    ET.register_namespace("gx", GX)
    ET.register_namespace("atom", ATOM)
    members["doc.kml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for name, contents in members.items():
            archive.writestr(name, contents)

    print(f"Created {destination}")
    print(f"Final Hub areas: {len(areas)}")
    print(f"Repositioned Hub centers: {len(centers)}")
    print(f"Covered area: {domain.area / 1_000_000:.2f} square kilometres")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    rebuild(arguments.source, arguments.destination)


if __name__ == "__main__":
    main()
