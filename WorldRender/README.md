# WorldRender

A Python high-level library for rendering persistent world-space overlays in Minecraft 1.21.11 using the Gizmos API. Supports boxes, blocks, floating text, points, lines, arrows, circles, and quads — all rendered see-through (always on top) by default but can be changed.

---

## Requirements

- Minecraft 1.21.11+
- [Minescript](https://minescript.net/) 5.0b11+
- Python 3.10+

---

## Setup

Place `worldrender.py` in your `minecraft/minescript/` directory and import it from any Python or Pyjinn script:

```python
from worldrender import WorldRender
```

The library self-initializes on import. No manual setup is required.

---

## How it works

All gizmos are registered in an internal dictionary and re-submitted to the Gizmos API on every render frame. Gizmos persist across frames until explicitly removed. The registry is capped at `max_size` entries per type (default `1024`); oldest entries are evicted automatically when the cap is exceeded.

Every `add_*` method returns an integer **ID** that can be used later to remove the gizmo without needing to remember its coordinates. Alternatively, all `remove_*` methods also accept the original coordinates directly.

---

## Color parameters

All gizmo methods accept `r`, `g`, `b`, `a` as separate `int` parameters in the range `0–255`. Alpha `255` is fully opaque, `0` is fully transparent.

```python
# Red, fully opaque
WorldRender.add_block(10, 64, 10, r=255, g=0, b=0)

# Cyan, semi-transparent
WorldRender.add_circle(0.0, 65.0, 0.0, 3.0, r=0, g=255, b=255, a=128)
```

---

## `always_on_top` parameter

All `add_*` methods accept an `always_on_top` boolean parameter (default `True`). When `True`, the gizmo renders through blocks and terrain. When `False`, the gizmo is occluded by geometry like any normal in-world object.

```python
# Renders through walls (default behavior)
WorldRender.add_block(10, 64, 10, r=255, g=0, b=0)

# Only visible when not behind a block
WorldRender.add_block(10, 64, 10, r=255, g=0, b=0, always_on_top=False)
```

---

## API Reference

### Boxes

Render a box between two diagonally opposite positions

---

#### `add_box`

```python
WorldRender.add_box(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x1`, `y1`, `z1` | `int` | Block grid position1. |
| `x2`, `y2`, `z2` | `int` | Block grid position2. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this box.

```python
box_id = WorldRender.add_box(10, 64, 10, 13, 67, 13, r=255, g=0, b=0)
box_id = WorldRender.add_box(10, 64, 10, 13, 67, 13, r=255, g=0, b=0, always_on_top=False)
```

---

#### `remove_box`

```python
WorldRender.remove_box(x1, y1, z1, x2, y2, z2)
WorldRender.remove_box(id=box_id)
```

Removes the box at the given coordinates, or by ID if `id` is provided.

```python
WorldRender.remove_box(10, 64, 10, 13, 67, 13)
WorldRender.remove_box(id=box_id)
```

---

#### `get_box_list`

```python
WorldRender.get_box_list() -> dict
```

Returns the internal registry of all active boxes.

- **Keys:** `int` IDs
- **Values:** `(x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_box_list().items():
    print(eid, entry)
```

---

### Blocks

Renders a 1×1×1 block-aligned outline around the block at the given integer coordinates.

---

#### `add_block`

```python
WorldRender.add_block(x, y, z, r=255, g=255, b=255, a=255, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x`, `y`, `z` | `int` | Block grid position. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this block.

```python
block_id = WorldRender.add_block(10, 64, 10, r=255, g=0, b=0)
block_id = WorldRender.add_block(10, 64, 10, r=255, g=0, b=0, always_on_top=False)
```

---

#### `remove_block`

```python
WorldRender.remove_block(x, y, z)
WorldRender.remove_block(id=block_id)
```

Removes the block at the given coordinates, or by ID if `id` is provided.

```python
WorldRender.remove_block(10, 64, 10)
WorldRender.remove_block(id=block_id)
```

---

#### `get_block_list`

```python
WorldRender.get_block_list() -> dict
```

Returns the internal registry of all active blocks.

- **Keys:** `int` IDs
- **Values:** `(x, y, z, r, g, b, a, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_block_list().items():
    print(eid, entry)
```

---

### Floating Text

Renders a billboard text label that always faces the camera.

---

#### `add_text`

```python
WorldRender.add_text(x, y, z, text, r=255, g=255, b=255, a=255, size=1.0, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x`, `y`, `z` | `float` | World-space position. |
| `text` | `str` | Text string to display. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `size` | `float` | Scale multiplier. Default: `1.0`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this text.

```python
text_id = WorldRender.add_text(10.5, 66.0, 10.5, "Hello!", r=255, g=255, b=0, size=1.5)
text_id = WorldRender.add_text(10.5, 66.0, 10.5, "Hidden", always_on_top=False)
```

---

#### `remove_text`

```python
WorldRender.remove_text(x, y, z)
WorldRender.remove_text(id=text_id)
```

```python
WorldRender.remove_text(10.5, 66.0, 10.5)
WorldRender.remove_text(id=text_id)
```

---

#### `get_text_list`

```python
WorldRender.get_text_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x, y, z, text, r, g, b, a, size, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_text_list().items():
    print(eid, entry)
```

---

### Points

Renders a colored dot at a world-space position.

---

#### `add_point`

```python
WorldRender.add_point(x, y, z, r=255, g=255, b=255, a=255, size=4.0, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x`, `y`, `z` | `float` | World-space position. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `size` | `float` | Rendered point size. Default: `4.0`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this point.

```python
pt_id = WorldRender.add_point(10.5, 64.5, 10.5, r=0, g=255, b=0, size=6.0)
pt_id = WorldRender.add_point(10.5, 64.5, 10.5, r=0, g=255, b=0, always_on_top=False)
```

---

#### `remove_point`

```python
WorldRender.remove_point(x, y, z)
WorldRender.remove_point(id=pt_id)
```

```python
WorldRender.remove_point(10.5, 64.5, 10.5)
WorldRender.remove_point(id=pt_id)
```

---

#### `get_point_list`

```python
WorldRender.get_point_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x, y, z, r, g, b, a, size, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_point_list().items():
    print(eid, entry)
```

---

### Lines

Renders a straight line segment between two world-space points.

---

#### `add_line`

```python
WorldRender.add_line(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, width=1.0, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x1`, `y1`, `z1` | `float` | Start point. |
| `x2`, `y2`, `z2` | `float` | End point. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `width` | `float` | Line width. Default: `1.0`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this line.

```python
line_id = WorldRender.add_line(0.0, 65.0, 0.0, 10.0, 65.0, 10.0, r=0, g=128, b=255, width=2.0)
line_id = WorldRender.add_line(0.0, 65.0, 0.0, 10.0, 65.0, 10.0, always_on_top=False)
```

---

#### `remove_line`

```python
WorldRender.remove_line(x1, y1, z1, x2, y2, z2)
WorldRender.remove_line(id=line_id)
```

> **Note:** When removing by coordinates, both endpoints must match exactly as passed to `add_line`.

```python
WorldRender.remove_line(0.0, 65.0, 0.0, 10.0, 65.0, 10.0)
WorldRender.remove_line(id=line_id)
```

---

#### `get_line_list`

```python
WorldRender.get_line_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_line_list().items():
    print(eid, entry)
```

---

### Arrows

Renders a directed arrow from a tail point to a head point.

---

#### `add_arrow`

```python
WorldRender.add_arrow(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, width=1.0, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x1`, `y1`, `z1` | `float` | Arrow tail (start). |
| `x2`, `y2`, `z2` | `float` | Arrow head (end). |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `width` | `float` | Shaft width. Default: `1.0`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this arrow.

```python
arrow_id = WorldRender.add_arrow(0.0, 65.0, 0.0, 5.0, 65.0, 0.0, r=255, g=128, b=0, width=2.0)
arrow_id = WorldRender.add_arrow(0.0, 65.0, 0.0, 5.0, 65.0, 0.0, always_on_top=False)
```

---

#### `remove_arrow`

```python
WorldRender.remove_arrow(x1, y1, z1, x2, y2, z2)
WorldRender.remove_arrow(id=arrow_id)
```

```python
WorldRender.remove_arrow(0.0, 65.0, 0.0, 5.0, 65.0, 0.0)
WorldRender.remove_arrow(id=arrow_id)
```

---

#### `get_arrow_list`

```python
WorldRender.get_arrow_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_arrow_list().items():
    print(eid, entry)
```

---

### Circles

Renders a circle (outline or filled disc) on a horizontal plane centered at the given position.

---

#### `add_circle`

```python
WorldRender.add_circle(x, y, z, radius, r=255, g=255, b=255, a=255, filled=False, always_on_top=True) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x`, `y`, `z` | `float` | Center position in world space. |
| `radius` | `float` | Radius in world units. |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `filled` | `bool` | `True` for filled disc, `False` for outline only. Default: `False`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this circle.

```python
circle_id = WorldRender.add_circle(0.0, 64.0, 0.0, 5.0, r=200, g=0, b=255, filled=True)
circle_id = WorldRender.add_circle(0.0, 64.0, 0.0, 5.0, always_on_top=False)
```

---

#### `remove_circle`

```python
WorldRender.remove_circle(x, y, z)
WorldRender.remove_circle(id=circle_id)
```

```python
WorldRender.remove_circle(0.0, 64.0, 0.0)
WorldRender.remove_circle(id=circle_id)
```

---

#### `get_circle_list`

```python
WorldRender.get_circle_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x, y, z, radius, r, g, b, a, filled, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_circle_list().items():
    print(eid, entry)
```

---

### Rectangles (Quads)

Renders an arbitrary planar quadrilateral defined by four world-space corner vertices.

---

#### `add_rect`

```python
WorldRender.add_rect(
    x1, y1, z1,
    x2, y2, z2,
    x3, y3, z3,
    x4, y4, z4,
    r=255, g=255, b=255, a=255, filled=False, always_on_top=True
) -> int
```

| Parameter | Type | Description |
|---|---|---|
| `x1,y1,z1` … `x4,y4,z4` | `float` | Four corners, in order (CW or CCW). |
| `r`, `g`, `b` | `int` | RGB color, 0–255. Default: `255`. |
| `a` | `int` | Alpha/opacity, 0–255. Default: `255`. |
| `filled` | `bool` | `True` for filled quad, `False` for outline only. Default: `False`. |
| `always_on_top` | `bool` | Render through blocks. Default: `True`. |

Returns the **ID** assigned to this rect.

> **Note:** Vertices must be coplanar and specified in consistent winding order (all clockwise or all counter-clockwise) for correct rendering.

```python
rect_id = WorldRender.add_rect(
    -1.0, 65.0,  1.0,
     1.0, 65.0,  1.0,
     1.0, 65.0, -1.0,
    -1.0, 65.0, -1.0,
    r=0, g=255, b=128, filled=True
)
rect_id = WorldRender.add_rect(
    -1.0, 65.0,  1.0,  1.0, 65.0,  1.0,
     1.0, 65.0, -1.0, -1.0, 65.0, -1.0,
    always_on_top=False
)
```

---

#### `remove_rect`

```python
WorldRender.remove_rect(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4)
WorldRender.remove_rect(id=rect_id)
```

> **Note:** When removing by coordinates, all four corners must match exactly as passed to `add_rect`.

```python
WorldRender.remove_rect(id=rect_id)
```

---

#### `get_rect_list`

```python
WorldRender.get_rect_list() -> dict
```

- **Keys:** `int` IDs
- **Values:** `(x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4, r, g, b, a, filled, always_on_top)` tuples

```python
for eid, entry in WorldRender.get_rect_list().items():
    print(eid, entry)
```

---

### Visibility & Toggle

Controls whether WorldRender content is visible, and optionally binds an in-game toggle key.

---

#### `show_wr`

```python
WorldRender.show_wr(enable: bool)
```

Shows or hides all rendered gizmos without clearing the registry. Useful for temporarily hiding the overlay without losing registered entries.

```python
WorldRender.show_wr(False)  # hide all gizmos
WorldRender.show_wr(True)   # show again
```

---

#### `use_toggle_key`

```python
WorldRender.use_toggle_key(enable: bool)
```

Enables or disables an in-game key listener that toggles visibility with a single keypress. The default key is **F12** (GLFW code `301`). When disabled, the key listener is removed.

```python
WorldRender.use_toggle_key(True)   # F12 now toggles the overlay
WorldRender.use_toggle_key(False)  # disable the toggle key
```

---

#### `set_toggle_key`

```python
WorldRender.set_toggle_key(toggle_key: int)
```

Changes the key used to toggle visibility. Takes a [GLFW key code](https://www.glfw.org/docs/3.3/group__keys.html). Must be called before or after `use_toggle_key(True)`.

```python
WorldRender.set_toggle_key(292)   # F3
WorldRender.use_toggle_key(True)
```

---

## Notes

### `always_on_top` per gizmo

Each gizmo independently controls whether it renders through geometry. This allows mixing occluded and see-through gizmos in the same scene:

```python
# Path line always visible through terrain
WorldRender.add_line(0.0, 64.0, 0.0, 10.0, 64.0, 0.0, r=0, g=255, b=0)

# Block always visible through terrain
WorldRender.add_block(10, 65, 10, r=128, g=0, b=0)

# Block only visible when in line of sight
WorldRender.add_block(10, 64, 10, r=255, g=0, b=0, always_on_top=False)
```

### ID-based vs coordinate-based removal

`add_*` always returns an `int` ID. For gizmos that require many coordinate arguments to identify (lines, arrows, rects), storing the ID and using `remove_*(id=...)` is strongly recommended:

```python
# Preferred for multi-coordinate gizmos
line_id = WorldRender.add_line(0.0, 65.0, 0.0, 10.0, 68.0, 5.0)
# ... later:
WorldRender.remove_line(id=line_id)
```

### Capacity limit

Each gizmo type has a shared capacity of `1024` entries (set internally). When the limit is exceeded, the oldest entry is automatically evicted. This limit applies per type — boxes, blocks, texts, lines, etc. each have their own `1024`-entry budget.

### Replacing a gizmo at the same position

Adding a gizmo at coordinates already occupied by an existing gizmo of the same type silently replaces it. The old entry is removed and a new ID is assigned:

```python
id1 = WorldRender.add_block(0, 64, 0, r=255, g=0, b=0)
id2 = WorldRender.add_block(0, 64, 0, r=0, g=255, b=0)  # replaces id1, id1 is now invalid
```

---

## License

MIT © 2026 RazrCraft
