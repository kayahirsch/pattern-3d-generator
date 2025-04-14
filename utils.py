import trimesh
import numpy as np

def load_model_and_flatten(obj_name):
    filepath = f"models/{obj_name}.glb"
    mesh = trimesh.load(filepath)

    # Handle scene objects by combining all geometry
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    # Safety check: if mesh is empty, return empty list
    if mesh.is_empty or mesh.vertices.shape[0] == 0:
        return []

    # 3D to 2D (drop z-axis)
    projection = mesh.vertices[:, :2]
    
    try:
        hull = trimesh.Trimesh(projection).convex_hull
        return [(float(x), float(y)) for x, y in hull.vertices]
    except:
        return []
