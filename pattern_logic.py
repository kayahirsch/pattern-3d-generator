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
    scale = 5  # Adjust for SVG fit
    combined -= combined.min(axis=0)
    combined *= scale

    # Compute alpha shape (concave hull) for shrinkwrap effect
    alpha = 0.2 * np.linalg.norm(combined.max(axis=0) - combined.min(axis=0))
    hull_shape = alphashape.alphashape(combined, alpha)

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=('1000px', '1000px'))

    if isinstance(hull_shape, Polygon):
        polygons = [hull_shape]
    elif isinstance(hull_shape, MultiPolygon):
        polygons = list(hull_shape.geoms)
    else:
        raise ValueError("Could not create valid hull shape")

    for poly in polygons:
        points = np.array(poly.exterior.coords)
        dwg.add(dwg.polygon(
            points=[(x, y) for x, y in points],
            stroke="black",
            fill="none",
            stroke_width=2
        ))

        if include_seam_allowance:
            offset = poly.buffer(10)  # seam allowance
            if isinstance(offset, Polygon):
                dwg.add(dwg.polygon(
                    points=[(x, y) for x, y in offset.exterior.coords],
                    stroke="red",
                    fill="none",
                    stroke_dasharray="4,2"
                ))
            elif isinstance(offset, MultiPolygon):
                for p in offset.geoms:
                    dwg.add(dwg.polygon(
                        points=[(x, y) for x, y in p.exterior.coords],
                        stroke="red",
                        fill="none",
                        stroke_dasharray="4,2"
                    ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
