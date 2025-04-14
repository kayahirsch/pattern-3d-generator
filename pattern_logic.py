import os
import svgwrite
import trimesh
import numpy as np
from shapely.geometry import MultiPoint
from shapely.ops import unary_union
import alphashape

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
            if mesh.vertices.shape[0] == 0:
                continue
            mesh.vertices[:, 2] = 0
            points = mesh.vertices[:, :2]
            all_points.append(points)
        except Exception as e:
            print(f"Error loading {obj}: {e}")
            continue

    if not all_points:
        raise ValueError("No valid objects loaded.")

    all_points = np.concatenate(all_points)
    all_points -= np.min(all_points, axis=0)
    scale = 500 / np.max(all_points.max(axis=0))
    all_points *= scale

    hull_shape = alphashape.alphashape(all_points, alpha=1.5)
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=("800px", "800px"))

    # Draw shrinkwrap outline
    if isinstance(hull_shape, MultiPoint):  # Fallback
        hull_shape = hull_shape.convex_hull

    hull_coords = list(hull_shape.exterior.coords)
    dwg.add(dwg.polygon(
        points=hull_coords,
        stroke='black',
        fill='none',
        stroke_width=2
    ))

    # Optional seam allowance (buffer)
    seam_allowance = 10  # units
    if include_straps:
        seam = hull_shape.buffer(seam_allowance)
        if hasattr(seam, "exterior"):
            dwg.add(dwg.polygon(
                points=list(seam.exterior.coords),
                stroke='red',
                fill='none',
                stroke_dasharray="4,2"
            ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
