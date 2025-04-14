import os
import svgwrite
import trimesh
import numpy as np
import alphashape
from shapely.geometry import Polygon
from shapely.affinity import scale as scale_polygon

def generate_pattern_svg(object_list, include_straps=False, return_string=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    all_points = []

    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        print(f"Loading: {file_path}")
        try:
            mesh = trimesh.load(file_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
            mesh.vertices[:, 2] = 0  # flatten
            all_points.append(mesh.vertices[:, :2])
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    if not all_points:
        raise ValueError("No valid 3D models loaded.")

    all_points = np.vstack(all_points)
    min_corner = all_points.min(axis=0)
    all_points -= min_corner

    max_dim = 600  # max pattern width/height
    size = all_points.max(axis=0)
    scale = max_dim / np.max(size)
    all_points *= scale

    # Create the alphashape (adjust alpha for smoothness)
    alpha = 0.3
    shape = alphashape.alphashape(all_points, alpha)
    if shape.geom_type != 'Polygon':
        raise ValueError("Alpha shape did not produce a polygon.")

    # Create SVG
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(max_dim + 200, max_dim + 200))

    # Draw bag outline
    poly_pts = list(shape.exterior.coords)
    dwg.add(dwg.polygon(
        points=[(x + 100, y + 100) for x, y in poly_pts],
        stroke='black',
        fill='none',
        stroke_width=2
    ))

    # Optional straps (top outline)
    if include_straps:
        straps = scale_polygon(shape, xfact=0.8, yfact=0.1, origin='center')
        if isinstance(straps, Polygon):
            dwg.add(dwg.polygon(
                points=[(x + 100, y + 100) for x, y in straps.exterior.coords],
                stroke='blue',
                fill='none',
                stroke_dasharray="5,5"
            ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
