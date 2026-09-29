# Standardized Architectural Floor-Plan Representation

This document defines the official standardized JSON geometry representation used across the Generative AI (GAN & VAE) pipeline, preprocessing scripts, layout validators, and the SVG 2D blueprint renderer.

---

## 1. Schema Overview

The floor plan is represented as a structured dictionary containing building-level metadata and a vector list of rectangular bounding rooms.

```json
{
  "building_type": "library",
  "building_width": 30.0,
  "building_length": 20.0,
  "floors_count": 1,
  "rooms": [
    {
      "id": 1,
      "type": "reading_hall",
      "name": "Reading Hall",
      "x": 0.0,
      "y": 0.0,
      "width": 15.0,
      "height": 10.0,
      "is_nested": false
    },
    {
      "id": 2,
      "type": "computer_section",
      "name": "Computer Section",
      "x": 15.0,
      "y": 0.0,
      "width": 15.0,
      "height": 10.0,
      "is_nested": false
    }
  ]
}
```

---

## 2. Field Specifications

| Field | Type | Description |
| :--- | :--- | :--- |
| `building_type` | `string` | Semantic typology (e.g., `library`, `hospital`, `house`, `office`, `school`, `mall`, `museum`). |
| `building_width` | `float` | Total horizontal width of building boundary (meters). |
| `building_length` | `float` | Total vertical length/depth of building boundary (meters). |
| `floors_count` | `int` | Total stories (default: `1` for 2D focus). |
| `rooms` | `list[object]` | Array of room bounding specifications. |

### Room Specification Object
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | `int` | Unique room index. |
| `type` | `string` | Semantic category key (e.g., `reading_hall`, `toilet`, `corridor`, `office`). |
| `name` | `string` | Human-readable label for rendering. |
| `x` | `float` | Top-left X coordinate in meters (`0.0` to `building_width`). |
| `y` | `float` | Top-left Y coordinate in meters (`0.0` to `building_length`). |
| `width` | `float` | Room horizontal dimension in meters. |
| `height` | `float` | Room vertical dimension in meters. |
| `is_nested` | `boolean` | Flag indicating internal core / service space placement. |

---

## 3. Tensor / Matrix Encoding for Machine Learning

For VAE and CGAN training, the continuous coordinate representation is encoded into a normalized vector tensor $X \in \mathbb{R}^{N \times K}$ or a discretized semantic grid map $M \in \mathbb{R}^{C \times H \times W}$:

1. **Vector Tensor Encoding**:
   - Up to $N$ rooms per plan (padded with zeros).
   - Per room features: $[x_{\text{norm}}, y_{\text{norm}}, w_{\text{norm}}, h_{\text{norm}}, \text{one\_hot}(\text{type})]$
   - Normalized coordinates: $x_{\text{norm}} = x / W_{\text{building}}$, $y_{\text{norm}} = y / L_{\text{building}}$.

2. **Conditioning Vector ($C$)**:
   - One-hot encoding of `building_type` concatenated with $[W_{\text{norm}}, L_{\text{norm}}, \text{target\_room\_counts}]$.

3. **Reconstruction**:
   - The model output vectors are un-normalized back to physical dimensions $[0, W_{\text{building}}]$ and $[0, L_{\text{building}}]$ before passing to the Layout Validator and SVG Renderer.
