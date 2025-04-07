import os
import svgwrite
from utils import load_model_and_flatten

OUTPUT_DIR = "patterns"

def generate_pattern_svg(objects, include_straps=False):
    filename = os.path.join(OUTPUT_DIR, "pattern.svg")
    dwg = svgwrite.Drawing(filename, profile='tiny', size=("300mm", "300mm"))

    offset_x = 0
    for obj in objects:
        flattened = load_model_and_flatten(obj)
        points = [(x + offset_x, y) for x, y in flattened]
        dwg.add(dwg.polygon(points=points, stroke="black", fill="none", stroke_width=1))
        dwg.add(dwg.text(obj, insert=(points[0][0], points[0][1] - 5)))
        offset_x += 100

    # Scale box
    dwg.add(dwg.text("1cm scale box:", insert=(10, 290)))
    dwg.add(dwg.rect(insert=(100, 280), size=(10, 10), stroke="black", fill="none"))

    if include_straps:
        dwg.add(dwg.rect(insert=(offset_x, 0), size=(20, 200), stroke="blue", fill="none"))
        dwg.add(dwg.text("Strap", insert=(offset_x, 220)))

    dwg.save()
    return filename
