# 3D-to-2D Sewing Pattern Generator

Generate SVG sewing patterns from 3D models of everyday items using shrinkwrap projection.

## Endpoints

- `POST /generate-pattern`:
  ```json
  {
    "objects": ["phone", "book", "lipstick"],
    "include_straps": true
  }
