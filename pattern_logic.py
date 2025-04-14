import os
import svgwrite
import trimesh
import numpy as np
from scipy.spatial import ConvexHull

def generate_pattern_svg(object_list, include_straps=False, return_string=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    all_vertices = []

    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        print(f"Attempting to load: {file_path}")

        try:
            mesh = trimesh.load(file_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
            if mesh.vertices.shape[0] == 0:
                continue
            mesh.vertices[:, 2] = 0
            all_vertices.append(mesh.vertices[:, :2])
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            import traceback
            traceback.print_exc()
            continue

    if not all_vertices:
        raise ValueError("No valid meshes found.")

    combined_vertices = np.vstack(all_vertices)
    hull = ConvexHull(combined_vertices)

    min_corner = combined_vertices.min(axis=0)
    max_corner = combined_vertices.max(axis=0)
    size = max_corner - min_corner
    scale = 800 / np.max(size)
    scaled_vertices = (combined_vertices - min_corner) * scale

    svg_size = (scaled_vertices[:, 0].max() + 200, scaled_vertices[:, 1].max() + 200)
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=svg_size)

    hull_points = scaled_vertices[hull.vertices]
    dwg.add(dwg.polygon(
        points=[(pt[0] + 100, pt[1] + 100) for pt in hull_points],
        stroke='black',
        fill='none',
        stroke_width=2
    ))

    if include_straps:
        centroid = hull_points.mean(axis=0) + 100
        dwg.add(dwg.rect(
            insert=(centroid[0] - 10, centroid[1] - 80),
            size=(20, 60),
            stroke='black',
            fill='none',
            stroke_dasharray="5,5"
        ))
        dwg.add(dwg.rect(
            insert=(centroid[0] - 10, centroid[1] + 20),
            size=(20, 60),
            stroke='black',
            fill='none',
            stroke_dasharray="5,5"
        ))

    if return_string:
        return dwg.tostring()
    else:
        dwg.save()
        return output_path
