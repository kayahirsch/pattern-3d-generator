import os
import svgwrite
import trimesh
import numpy as np
import alphashape
from shapely.geometry import MultiPoint, Polygon, MultiPolygon

def generate_pattern_svg(object_list, include_seam_allowance=False, return_string=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    all_vertices = []

    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        print(f"Loading: {file_path}")

        try:
            mesh = trimesh.load(file_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
            if mesh.vertices.shape[0] == 0:
                continue
            mesh.vertices[:, 2] = 0  # Flatten to 2D
            vertices = mesh.vertices[:, :2]
            all_vertices.append(vertices)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            continue

    if not all_vertices:
        raise ValueError("No valid objects found")

    combined = np.vstack(all_vertices)

    # Generate alpha shape (shrinkwrap) and smooth hull
    alpha = 0.2 * np.linalg.norm(combined.max(axis=0) - combined.min(axis=0))
    hull_shape = alphashape.alphashape(combined, alpha)

    # Prepare SVG canvas
    canvas_size = 1000
    minx, miny, maxx, maxy = hull_shape.bounds
    width, height = maxx - minx, maxy - miny
    scale = canvas_size / max(width, height)
    dx = (canvas_size - width * scale) / 2
    dy = (canvas_size - height * scale) / 2

    def transform_coords(coords):
        return [((x - minx) * scale + dx, (y - miny) * scale + dy) for x, y in coords]

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(canvas_size, canvas_size))

    polygons = []
    if isinstance(hull_shape, Polygon):
        polygons = [hull_shape]
    elif isinstance(hull_shape, MultiPolygon):
        polygons = list(hull_shape.geoms)

    # Draw bag outline
    for poly in polygons:
        dwg.add(dwg.polygon(
            points=transform_coords(poly.exterior.coords),
            stroke="black",
            fill="none",
            stroke_width=2
        ))

        # Optional seam allowance
        if include_seam_allowance:
            offset = poly.buffer(10)
            if isinstance(offset, Polygon):
                dwg.add(dwg.polygon(
                    points=transform_coords(offset.exterior.coords),
                    stroke="red",
                    fill="none",
                    stroke_dasharray="4,2"
                ))
            elif isinstance(offset, MultiPolygon):
                for p in offset.geoms:
                    dwg.add(dwg.polygon(
                        points=transform_coords(p.exterior.coords),
                        stroke="red",
                        fill="none",
                        stroke_dasharray="4,2"
                    ))

    return dwg.tostring() if return_string else dwg.save() or output_path
