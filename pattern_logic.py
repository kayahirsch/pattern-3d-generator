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

    # Combine and center the coordinates
    combined = np.vstack(all_vertices)
    combined -= combined.mean(axis=0)  # Center around origin

    # Shrinkwrap shape
    alpha = 0.2 * np.linalg.norm(combined.ptp(axis=0))  # better alpha guess
    hull_shape = alphashape.alphashape(combined, alpha)

    # Calculate bounds for scaling
    bounds = hull_shape.bounds
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny

    canvas_size = 1000
    padding = 50
    scale = (canvas_size - 2 * padding) / max(width, height)

    def transform_coords(coords):
        return [(
            (x - minx) * scale + padding,
            (canvas_size - padding) - (y - miny) * scale  # flip Y for SVG
        ) for x, y in coords]

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(canvas_size, canvas_size))

    if isinstance(hull_shape, Polygon):
        polygons = [hull_shape]
    elif isinstance(hull_shape, MultiPolygon):
        polygons = list(hull_shape.geoms)
    else:
        raise ValueError("Invalid hull shape")

    # Main hull
    for poly in polygons:
        dwg.add(dwg.polygon(
            points=transform_coords(poly.exterior.coords),
            stroke="black",
            fill="none",
            stroke_width=2
        ))

        # Optional: Seam allowance
        if include_seam_allowance:
            offset = poly.buffer(10)
            shapes = [offset] if isinstance(offset, Polygon) else offset.geoms
            for seam_poly in shapes:
                dwg.add(dwg.polygon(
                    points=transform_coords(seam_poly.exterior.coords),
                    stroke="red",
                    fill="none",
                    stroke_dasharray="6,4"
                ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
