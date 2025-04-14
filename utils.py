import trimesh
import numpy as np

def load_model_and_flatten(obj_name):
    filepath = f"models/{obj_name}.glb"
    try:
        mesh = trimesh.load(filepath)

        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

        if mesh.is_empty or mesh.vertices.shape[0] == 0:
            return []

        projection = mesh.vertices[:, :2]
        hull = trimesh.Trimesh(projection).convex_hull

        return [(float(x), float(y)) for x, y in hull.vertices]
    except Exception as e:
        print(f"Error loading {obj_name}: {e}")
        return []

