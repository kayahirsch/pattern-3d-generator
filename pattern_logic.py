import os
import svgwrite
import trimesh
import numpy as np
import alphashape
from shapely.geometry import Polygon, MultiPolygon

def generate_pattern_svg(object_list, include_seam_allowance=False, return_string=False, buffer_size=10):
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

    # Compute alpha shape
    alpha = 0.2 * np.linalg.norm(np.ptp(combined, axis=0))
    hull_shape = alphashape.alphashape(combined, alpha)
    if hull_shape is None:
        raise ValueError("Failed to generate hull.")

    # If seam allowance is on, expand shape now so we can scale both it and the main shape properly
    draw_shape = hull_shape
    if include_seam_allowance:
        draw_shape = hull_shape.buffer(buffer_size)

    # Canvas setup
    canvas_size = 1200
    padding = 100
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(f"{canvas_size}px", f"{canvas_size}px"))

    # Compute scaling from draw_shape bounds
    minx, miny, maxx, maxy = draw_shape.bounds
    shape_width = maxx - minx
    shape_height = maxy - miny
    scale_x = (canvas_size - 2 * padding) / shape_width
    scale_y = (canvas_size - 2 * padding) / shape_height
    scale = min(scale_x, scale_y)

    translate_x = (canvas_size - shape_width * scale) / 2 - minx * scale
    translate_y = (canvas_size - shape_height * scale) / 2 - miny * scale

    def transform(coords):
        return [((x * scale) + translate_x, (y * scale) + translate_y) for x, y in coords]

    # Split MultiPolygon or handle Polygon
    polygons = [hull_shape] if isinstance(hull_shape, Polygon) else list(hull_shape.geoms)

    for poly in polygons:
        if include_seam_allowance:
            offset = poly.buffer(buffer_size)
            offset_polys = [offset] if isinstance(offset, Polygon) else list(offset.geoms)
            for p in offset_polys:
                dwg.add(dwg.polygon(
                    points=transform(p.exterior.coords),
                    stroke="red",
                    fill="none",
                    stroke_dasharray="6,3",
                    stroke_width=1
                ))

        dwg.add(dwg.polygon(
            points=transform(poly.exterior.coords),
            stroke="black",
            fill="none",
            stroke_width=2
        ))

    return dwg.tostring() if return_string else dwg.save()
