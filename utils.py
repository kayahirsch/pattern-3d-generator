import trimesh
import numpy as np

def load_model_and_flatten(obj_name):
    filepath = f"models/{obj_name}.glb"
    mesh = trimesh.load(filepath)

    # Handle scene objects by combining all geometry
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    projection = mesh.vertices[:, :2]  # drop z-axis
    hull = trimesh.Trimesh(projection).convex_hull
    return [(float(x), float(y)) for x, y in hull.vertices]
