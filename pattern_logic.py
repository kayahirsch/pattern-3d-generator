import trimesh
import numpy as np
import svgwrite
import os

MODEL_DIR = "models"
OUTPUT_DIR = "patterns"

def load_mesh(filepath):
    mesh = trimesh.load(filepath)

    # Handle scene objects like those from GLB files
    if isinstance(mesh, trimesh.Scene):
        if not mesh.geometry:
            raise ValueError(f"{filepath} loaded as empty Scene")
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    if mesh.is_empty:
        raise ValueError(f"Mesh from {filepath} is empty")

    return mesh

def generate_pattern_svg(object_names, include_straps=False):
    if not object_names:
        raise ValueError("No objects selected")

    meshes = []
    for name in object_names:
        filepath = os.path.join(MODEL_DIR, name + ".glb")
        try:
            mesh = load_mesh(filepath)
            meshes.append(mesh)
        except Exception as e:
            print(f"Error loading {name}: {e}")
            continue

    if not meshes:
        raise ValueError("No valid meshes could be loaded")

    # Combine all meshes into one
    full_mesh = trimesh.util.concatenate(meshes)

    # Get bounding box for layout
    bounds = full_mesh.bounds
    width = bounds[1][0] - bounds[0][0]
    height = bounds[1][1] - bounds[0][1]

    # Convert to a simple flattened 2D projection
    flat = full_mesh.copy()
    flat.vertices[:, 2] = 0  # Flatten in Z direction

    # Create SVG drawing
    svg_path = os.path.join(OUTPUT_DIR, "pattern.svg")
    dwg = svgwrite.Drawing(svg_path, size=(f"{width+100}mm", f"{height+100}mm"))

    for face in flat.faces:
        points = [flat.vertices[i][:2] for i in face]
        dwg.add(dwg.polygon(points=points, fill="none", stroke="black"))

    # Optional strap outline
    if include_straps:
        dwg.add(dwg.rect(insert=(10, 10), size=("100mm", "20mm"),
                         fill="none", stroke="red"))
    
    # Labels for selected objects
    for i, name in enumerate(object_names):
        dwg.add(dwg.text(name, insert=(10, height + 40 + i * 20), fill="blue"))

    # Save SVG file
    dwg.save()
    return svg_path
