import os
import svgwrite
import trimesh
import numpy as np

def generate_pattern_svg(object_list, include_straps=False):
    OUTPUT_DIR = "patterns"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "pattern.svg")

    meshes = []
    for obj in object_list:
        file_path = os.path.join("models", f"{obj}.glb")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")
        mesh = trimesh.load(file_path)
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
        meshes.append((mesh, obj))

    spacing = 150
    max_dim = 100
    margin = 100
    cell_width = max_dim + spacing
    num_cols = 3

    processed = []
    for mesh, label in meshes:
        if mesh.vertices.shape[0] == 0:
            continue
        mesh.vertices[:, 2] = 0
        vertices = mesh.vertices[:, :2]

        min_corner = vertices.min(axis=0)
        max_corner = vertices.max(axis=0)
        size = max_corner - min_corner
        scale = max_dim / np.max(size)
        vertices = (vertices - min_corner) * scale

        processed.append((vertices, mesh.faces, label, size * scale))

    num_items = len(processed)
    num_rows = (num_items + num_cols - 1) // num_cols
    svg_width = num_cols * cell_width
    svg_height = num_rows * cell_width

    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(svg_width + 2 * margin, svg_height + 2 * margin))

    # Add title at top center
    dwg.add(dwg.text(
        "🧵 Your Custom Bag Layout",
        insert=(svg_width / 2 + margin, 50),
        text_anchor="middle",
        font_size="28px",
        font_weight="bold",
        fill="black"
    ))

    # Draw items
    for idx, (vertices, faces, label, scaled_size) in enumerate(processed):
        col = idx % num_cols
        row = idx // num_cols

        x0 = margin + col * cell_width + (max_dim - scaled_size[0]) / 2
        y0 = margin + row * cell_width + (max_dim - scaled_size[1]) / 2 + 60  # +60 to leave room for the title

        offset_vertices = vertices + np.array([x0, y0])

        for face in faces:
            pts = offset_vertices[face]
            dwg.add(svgwrite.shapes.Polygon(
                points=[(pt[0], pt[1]) for pt in pts],
                stroke='black',
                fill='none'
            ))

        dwg.add(dwg.text(
            label,
            insert=(x0, y0 + scaled_size[1] + 20),
            font_size="16px",
            fill="blue"
        ))

    dwg.save()
    return output_path
