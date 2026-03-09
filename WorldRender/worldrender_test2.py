"""
    @author RazrCraft
    @create date 2026-03-08 22:17:04
    @modify date 2026-03-09 00:26:09
    @desc Test for WorldRender
 """
from time import sleep
from worldrender import WorldRender

# ── Constants ─────────────────────────────────────────────────────────────────
Y = 64   # Base height for all test gizmos

# ── add_* ─────────────────────────────────────────────────────────────────────
WorldRender.add_box(1, Y+1, 1, 4, Y+3, 4, r=255, g=64, b=64)
WorldRender.add_block(0, Y, 0, r=255, g=64, b=64)
WorldRender.add_text(0.5, Y + 2, 0.5, "Hello WorldRender!", r=255, g=255, b=64)
WorldRender.add_point(1.0, Y + 1, 0.0, r=64, g=255, b=64, size=6.0)
WorldRender.add_line(0.0, Y + 1, -2.0, 2.0, Y + 1, -2.0, r=64, g=128, b=255, width=2.0)
WorldRender.add_arrow(0.0, Y + 1, 2.0, 3.0, Y + 1, 2.0, r=255, g=128, b=64, width=2.0)
WorldRender.add_circle(0.0, Y + 1, -4.0, radius=2.5, r=200, g=64, b=255)
WorldRender.add_rect(
    -1.0, Y + 1,  4.0,
     1.0, Y + 1,  4.0,
     1.0, Y + 1,  6.0,
    -1.0, Y + 1,  6.0,
    r=64, g=255, b=200, filled=True
)

# ── get_*_list ────────────────────────────────────────────────────────────────
sleep(1)
print("=== box list ===")
print(WorldRender.get_box_list())

sleep(1)
print("=== block list ===")
print(WorldRender.get_block_list())

sleep(1)
print("=== text list ===")
print(WorldRender.get_text_list())

sleep(1)
print("=== point list ===")
print(WorldRender.get_point_list())

sleep(1)
print("=== line list ===")
print(WorldRender.get_line_list())

sleep(1)
print("=== arrow list ===")
print(WorldRender.get_arrow_list())

sleep(1)
print("=== circle list ===")
print(WorldRender.get_circle_list())

sleep(1)
print("=== rect list ===")
print(WorldRender.get_rect_list())

# ── remove_* (by coordinates) ─────────────────────────────────────────────────
sleep(3)

WorldRender.remove_box(1, Y+1, 1, 4, Y+3, 4)
WorldRender.remove_block(0, Y, 0)
WorldRender.remove_text(0.5, Y + 2, 0.5)
WorldRender.remove_point(1.0, Y + 1, 0.0)
WorldRender.remove_line(0.0, Y + 1, -2.0, 2.0, Y + 1, -2.0)
WorldRender.remove_arrow(0.0, Y + 1, 2.0, 3.0, Y + 1, 2.0)
WorldRender.remove_circle(0.0, Y + 1, -4.0)
WorldRender.remove_rect(
    -1.0, Y + 1,  4.0,
     1.0, Y + 1,  4.0,
     1.0, Y + 1,  6.0,
    -1.0, Y + 1,  6.0,
)

print("All gizmos removed.")
