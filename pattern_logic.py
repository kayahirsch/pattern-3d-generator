import os
import svgwrite
import trimesh
import numpy as np
import alphashape
from shapely.geometry import Polygon, MultiPolygon

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

    # Compute concave hull
    alpha = 0.2 * np.linalg.norm(np.ptp(combined, axis=0))
    hull_shape = alphashape.alphashape(combined, alpha)
    if hull_shape is None:
        raise ValueError("Failed to generate hull.")

    # Canvas settings
    canvas_size = 1200
    padding = 100
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(f"{canvas_size}px", f"{canvas_size}px"))

    # Get bounds of shape
    minx, miny, maxx, maxy = hull_shape.bounds
    shape_width = maxx - minx
    shape_height = maxy - miny

    # Determine scale to fit within canvas (consider padding)
    scale_x = (canvas_size - 2 * padding) / shape_width
    scale_y = (canvas_size - 2 * padding) / shape_height
    scale = min(scale_x, scale_y)

    # Translate to center
    translate_x = (canvas_size - shape_width * scale) / 2 - minx * scale
    translate_y = (canvas_size - shape_height * scale) / 2 - miny * scale

    def transform(coords):
        return [((x * scale) + translate_x, (y * scale) + translate_y) for x, y in coords]

    if isinstance(hull_shape, Polygon):
        polys = [hull_shape]
    elif isinstance(hull_shape, MultiPolygon):
        polys = list(hull_shape.geoms)
    else:
        raise ValueError("Invalid geometry")

    for poly in polys:
        # Optional seam allowance (red dashed)
        if include_seam_allowance:
            offset = poly.buffer(10)
            offset_polys = [offset] if isinstance(offset, Polygon) else list(offset.geoms)
            for op in offset_polys:
                dwg.add(dwg.polygon(
                    points=transform(op.exterior.coords),
                    stroke="red",
                    fill="none",
                    stroke_dasharray="6,3",
                    stroke_width=1
                ))

        # Main shape outline (black solid)
        dwg.add(dwg.polygon(
            points=transform(poly.exterior.coords),
            stroke="black",
            fill="none",
            stroke_width=2
        ))

    return dwg.tostring() if return_string else dwg.save()
