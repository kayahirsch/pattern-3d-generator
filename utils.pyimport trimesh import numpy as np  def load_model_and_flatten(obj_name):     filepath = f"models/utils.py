import trimesh
import numpy as np

def load_model_and_flatten(obj_name):
    filepath = f"models/{obj_name}.glb"
    mesh = trimesh.load(filepath)
    projection = mesh.vertices[:, :2]  # 3D to 2D (drop z-axis)
    hull = trimesh.Trimesh(projection).convex_hull
    return [(float(x), float(y)) for x, y in hull.vertices]
