import os
import svgwrite
import trimesh
import numpy as np
from scipy.spatial import ConvexHull

def generate_pattern_svg(object_list, include_straps=False, return_string=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    meshes = []

    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        print(f"Attempting to load: {file_path}")

        try:
            mesh = trimesh.load(file_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
            meshes.append(mesh)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    if not meshes:
        raise ValueError("No valid meshes loaded.")

    combined_mesh = trimesh.util.concatenate(meshes)
    combined_mesh.vertices[:, 2] = 0
    points_2d = combined_mesh.vertices[:, :2]

    # Normalize and scale
    min_corner = points_2d.min(axis=0)
    max_corner = points_2d.max(axis=0)
    size = max_corner - min_corner
    scale = 400 / np.max(size)
    points_2d = (points_2d - min_corner) * scale

    # Create shrinkwrap pattern using ConvexHull
    hull = ConvexHull(points_2d)
    hull_points = points_2d[hull.vertices]

    svg_size = (600, 600)
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=svg_size)

    dwg.add(dwg.text(
        "🧵 Your Custom Bag Pattern",
        insert=(svg_size[0] / 2, 50),
        text_anchor="middle",
        font_size="24px",
        font_weight="bold"
    ))

    # Add shrinkwrap outline
    dwg.add(svgwrite.shapes.Polygon(
        points=[(pt[0] + 100, pt[1] + 100) for pt in hull_points],
        stroke='black',
        fill='none',
        stroke_width=2
    ))

    # Optional strap indicators
    if include_straps:
        strap_length = 60
        strap_width = 10
        x, y = hull_points[0]
        dwg.add(svgwrite.shapes.Rect(
            insert=(x + 100, y + 100 + 20),
            size=(strap_width, strap_length),
            fill='black'
        ))
        dwg.add(svgwrite.shapes.Rect(
            insert=(x + 180, y + 100 + 20),
            size=(strap_width, strap_length),
            fill='black'
        ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
