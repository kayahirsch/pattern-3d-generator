import os
import svgwrite
import trimesh
import numpy as np
import alphashape
from shapely.geometry import Polygon

def generate_pattern_svg(object_list, include_straps=False, return_string=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    meshes = []
    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        try:
            mesh = trimesh.load(file_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
            meshes.append(mesh)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    if not meshes:
        raise ValueError("No valid meshes found.")

    # Combine and flatten all vertices
    all_points = []
    for mesh in meshes:
        if mesh.vertices.shape[0] > 0:
            mesh.vertices[:, 2] = 0
            all_points.extend(mesh.vertices[:, :2])

    if not all_points:
        raise ValueError("No 2D vertices found.")

    points = np.array(all_points)

    # Normalize and scale
    min_corner = points.min(axis=0)
    size = points.max(axis=0) - min_corner
    scale = 600 / np.max(size)
    points = (points - min_corner) * scale

    # Generate the alpha shape (shrinkwrap outline)
    alpha = 0.5  # Change to tighten or relax the fit
    shape = alphashape.alphashape(points, alpha)
    if not isinstance(shape, Polygon):
        raise ValueError("Alpha shape did not return a valid polygon.")

    outline = [(x + 60, y + 80) for x, y in shape.exterior.coords]

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=("800px", "800px"))
    dwg.add(dwg.text(
        "🧵 Your Custom Bag Pattern",
        insert=(400, 40),
        text_anchor="middle",
        font_size="24px",
        font_weight="bold"
    ))

    dwg.add(dwg.polygon(
        points=outline,
        stroke='black',
        fill='none',
        stroke_width=2
    ))

    if include_straps:
        center_x = np.mean([pt[0] for pt in outline])
        bottom_y = max([pt[1] for pt in outline])
        dwg.add(dwg.rect(
            insert=(center_x - 40, bottom_y + 20),
            size=(80, 20),
            stroke='black',
            fill='none',
            stroke_dasharray="5,5"
        ))
        dwg.add(dwg.text(
            "Strap Outline",
            insert=(center_x, bottom_y + 55),
            text_anchor="middle",
            font_size="14px",
            fill="gray"
        ))

    return dwg.tostring() if return_string else dwg.save() or output_path
