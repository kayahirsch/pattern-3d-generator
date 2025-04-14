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

    # Compute alpha shape (concave hull) for shrinkwrap effect
    alpha = 0.2 * np.linalg.norm(combined.max(axis=0) - combined.min(axis=0))
    hull_shape = alphashape.alphashape(combined, alpha)

    # Prepare for scaling and translation to center in SVG
    canvas_size = 1000
    minx, miny, maxx, maxy = hull_shape.bounds
    width = maxx - minx
    height = maxy - miny

    scale = canvas_size / max(width, height)
    dx = (canvas_size - width * scale) / 2
    dy = (canvas_size - height * scale) / 2

    def transform_coords(coords):
        return [((x - minx) * scale + dx, (y - miny) * scale + dy) for x, y in coords]

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(f'{canvas_size}px', f'{canvas_size}px'))

    def draw_shape(shape, stroke='black', dash=None):
        if isinstance(shape, Polygon):
            exterior = transform_coords(shape.exterior.coords)
            dwg.add(dwg.polygon(points=exterior, stroke=stroke, fill='none',
                                stroke_dasharray=dash if dash else None, stroke_width=2))
        elif isinstance(shape, MultiPolygon):
            for poly in shape.geoms:
                exterior = transform_coords(poly.exterior.coords)
                dwg.add(dwg.polygon(points=exterior, stroke=stroke, fill='none',
                                    stroke_dasharray=dash if dash else None, stroke_width=2))

    draw_shape(hull_shape, stroke='black')

    if include_seam_allowance:
        seam_offset = 10  # In the same units as your canvas
        buffered_shape = hull_shape.buffer(seam_offset)
        draw_shape(buffered_shape, stroke='red', dash="4,2")

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
