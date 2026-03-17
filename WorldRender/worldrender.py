"""
    @author RazrCraft
    @create date 2026-03-08 21:32:37
    @modify date 2026-03-09 01:55:56
    @desc World rendering for Minecraft 1.21.11+
 """
from typing import overload
from minescript import set_default_executor, script_loop
from java import eval_pyjinn_script

set_default_executor(script_loop)

# # # WORLDRENDER # # #
pyj_wr = eval_pyjinn_script(r"""

def _check_ver(ver: str) -> bool:
    _mc_ver = version_info().minecraft
    mc_version = [int(v) for v in _mc_ver.split(".")]
    ver_parts  = [int(v) for v in ver.split(".")]
    check = True
    for i in range(3):
        check = check and mc_version[i] >= ver_parts[i]
    return check

Minecraft          = JavaClass("net.minecraft.client.Minecraft")
BlockPos           = JavaClass("net.minecraft.core.BlockPos")
AABB               = JavaClass("net.minecraft.world.phys.AABB")
Gizmos             = JavaClass("net.minecraft.gizmos.Gizmos")
GizmoStyle         = JavaClass("net.minecraft.gizmos.GizmoStyle")
TextGizmo_Style    = JavaClass("net.minecraft.gizmos.TextGizmo$Style")
Vec3               = JavaClass("net.minecraft.world.phys.Vec3")
ARGB               = JavaClass("net.minecraft.util.ARGB")

toggle_key = 301   # F12
_toggle_listener = None
show = True
_next_id = 0

def _new_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id

class WorldRender:
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
        self.boxes       = {}   # {id: (x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top)}
        self.boxes_idx   = {}   # {(x1, y1, z1, x2, y2, z2): id}
        self.blocks      = {}   # {id: (x, y, z, r, g, b, a, always_on_top)}
        self.blocks_idx  = {}   # {(x, y, z): id}
        self.texts       = {}   # {id: (x, y, z, text, r, g, b, a, size, always_on_top)}
        self.texts_idx   = {}   # {(x, y, z): id}
        self.points      = {}   # {id: (x, y, z, r, g, b, a, size, always_on_top)}
        self.points_idx  = {}   # {(x, y, z): id}
        self.lines       = {}   # {id: (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)}
        self.lines_idx   = {}   # {((x1,y1,z1),(x2,y2,z2)): id}
        self.arrows      = {}   # {id: (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)}
        self.arrows_idx  = {}   # {((x1,y1,z1),(x2,y2,z2)): id}
        self.circles     = {}   # {id: (x, y, z, radius, r, g, b, a, filled, always_on_top)}
        self.circles_idx = {}   # {(x, y, z): id}
        self.rects       = {}   # {id: (x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4, r, g, b, a, filled, always_on_top)}
        self.rects_idx   = {}   # {((x1,y1,z1),(x2,y2,z2),(x3,y3,z3),(x4,y4,z4)): id}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _evict(self, data: dict, idx: dict, key_fn) -> None:
        old_id, old_entry = next(iter(data.items()))
        del idx[key_fn(old_entry)]
        del data[old_id]

    def _remove_by_id(self, data: dict, idx: dict, key_fn, eid: int) -> None:
        entry = data[eid]
        del idx[key_fn(entry)]
        del data[eid]

    def _remove_by_key(self, data: dict, idx: dict, coords_key) -> None:
        eid = idx[coords_key]
        del idx[coords_key]
        del data[eid]

    # ── Boxes ─────────────────────────────────────────────────────────────────

    def add_box(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int,
                r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                always_on_top: bool = True) -> int:
        key = (x1, y1, z1, x2, y2, z2)
        if key in self.boxes_idx:
            del self.boxes[self.boxes_idx[key]]
            del self.boxes_idx[key]
        eid = _new_id()
        self.boxes[eid] = (x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top)
        self.boxes_idx[key] = eid
        if len(self.boxes) > self.max_size:
            self._evict(self.boxes, self.boxes_idx, lambda e: (e[0], e[1], e[2], e[3], e[4], e[5]))
        return eid

    def remove_box(self, x1: int = None, y1: int = None, z1: int = None,
                   x2: int = None, y2: int = None, z2: int = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.boxes, self.boxes_idx, lambda e: (e[0], e[1], e[2], e[3], e[4], e[5]), id)
        else:
            self._remove_by_key(self.boxes, self.boxes_idx, (x1, y1, z1, x2, y2, z2))

    def get_box_list(self) -> dict:
        return self.boxes

    # ── Blocks ─────────────────────────────────────────────────────────────────

    def add_block(self, x: int, y: int, z: int,
                r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                always_on_top: bool = True) -> int:
        key = (x, y, z)
        if key in self.blocks_idx:
            del self.blocks[self.blocks_idx[key]]
            del self.blocks_idx[key]
        eid = _new_id()
        self.blocks[eid] = (x, y, z, r, g, b, a, always_on_top)
        self.blocks_idx[key] = eid
        if len(self.blocks) > self.max_size:
            self._evict(self.blocks, self.blocks_idx, lambda e: (e[0], e[1], e[2]))
        return eid

    def remove_block(self, x: int = None, y: int = None, z: int = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.blocks, self.blocks_idx, lambda e: (e[0], e[1], e[2]), id)
        else:
            self._remove_by_key(self.blocks, self.blocks_idx, (x, y, z))

    def get_block_list(self) -> dict:
        return self.blocks

    # ── Texts ─────────────────────────────────────────────────────────────────

    def add_text(self, x: float, y: float, z: float, text: str,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 size: float = 1.0, always_on_top: bool = True) -> int:
        key = (x, y, z)
        if key in self.texts_idx:
            del self.texts[self.texts_idx[key]]
            del self.texts_idx[key]
        eid = _new_id()
        self.texts[eid] = (x, y, z, text, r, g, b, a, size, always_on_top)
        self.texts_idx[key] = eid
        if len(self.texts) > self.max_size:
            self._evict(self.texts, self.texts_idx, lambda e: (e[0], e[1], e[2]))
        return eid

    def remove_text(self, x: float = None, y: float = None, z: float = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.texts, self.texts_idx, lambda e: (e[0], e[1], e[2]), id)
        else:
            self._remove_by_key(self.texts, self.texts_idx, (x, y, z))

    def get_text_list(self) -> dict:
        return self.texts

    # ── Points ────────────────────────────────────────────────────────────────

    def add_point(self, x: float, y: float, z: float,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                  size: float = 4.0, always_on_top: bool = True) -> int:
        key = (x, y, z)
        if key in self.points_idx:
            del self.points[self.points_idx[key]]
            del self.points_idx[key]
        eid = _new_id()
        self.points[eid] = (x, y, z, r, g, b, a, size, always_on_top)
        self.points_idx[key] = eid
        if len(self.points) > self.max_size:
            self._evict(self.points, self.points_idx, lambda e: (e[0], e[1], e[2]))
        return eid

    def remove_point(self, x: float = None, y: float = None, z: float = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.points, self.points_idx, lambda e: (e[0], e[1], e[2]), id)
        else:
            self._remove_by_key(self.points, self.points_idx, (x, y, z))

    def get_point_list(self) -> dict:
        return self.points

    # ── Lines ─────────────────────────────────────────────────────────────────

    def add_line(self, x1: float, y1: float, z1: float,
                 x2: float, y2: float, z2: float,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 width: float = 1.0, always_on_top: bool = True) -> int:
        key = ((x1, y1, z1), (x2, y2, z2))
        if key in self.lines_idx:
            del self.lines[self.lines_idx[key]]
            del self.lines_idx[key]
        eid = _new_id()
        self.lines[eid] = (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)
        self.lines_idx[key] = eid
        if len(self.lines) > self.max_size:
            self._evict(self.lines, self.lines_idx, lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5])))
        return eid

    def remove_line(self, x1: float = None, y1: float = None, z1: float = None,
                    x2: float = None, y2: float = None, z2: float = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.lines, self.lines_idx, lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5])), id)
        else:
            self._remove_by_key(self.lines, self.lines_idx, ((x1, y1, z1), (x2, y2, z2)))

    def get_line_list(self) -> dict:
        return self.lines

    # ── Arrows ────────────────────────────────────────────────────────────────

    def add_arrow(self, x1: float, y1: float, z1: float,
                  x2: float, y2: float, z2: float,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                  width: float = 1.0, always_on_top: bool = True) -> int:
        key = ((x1, y1, z1), (x2, y2, z2))
        if key in self.arrows_idx:
            del self.arrows[self.arrows_idx[key]]
            del self.arrows_idx[key]
        eid = _new_id()
        self.arrows[eid] = (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)
        self.arrows_idx[key] = eid
        if len(self.arrows) > self.max_size:
            self._evict(self.arrows, self.arrows_idx, lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5])))
        return eid

    def remove_arrow(self, x1: float = None, y1: float = None, z1: float = None,
                     x2: float = None, y2: float = None, z2: float = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.arrows, self.arrows_idx, lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5])), id)
        else:
            self._remove_by_key(self.arrows, self.arrows_idx, ((x1, y1, z1), (x2, y2, z2)))

    def get_arrow_list(self) -> dict:
        return self.arrows

    # ── Circles ───────────────────────────────────────────────────────────────

    def add_circle(self, x: float, y: float, z: float, radius: float,
                   r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                   filled: bool = False, always_on_top: bool = True) -> int:
        key = (x, y, z)
        if key in self.circles_idx:
            del self.circles[self.circles_idx[key]]
            del self.circles_idx[key]
        eid = _new_id()
        self.circles[eid] = (x, y, z, radius, r, g, b, a, filled, always_on_top)
        self.circles_idx[key] = eid
        if len(self.circles) > self.max_size:
            self._evict(self.circles, self.circles_idx, lambda e: (e[0], e[1], e[2]))
        return eid

    def remove_circle(self, x: float = None, y: float = None, z: float = None, id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.circles, self.circles_idx, lambda e: (e[0], e[1], e[2]), id)
        else:
            self._remove_by_key(self.circles, self.circles_idx, (x, y, z))

    def get_circle_list(self) -> dict:
        return self.circles

    # ── Rects ─────────────────────────────────────────────────────────────────

    def add_rect(self,
                 x1: float, y1: float, z1: float,
                 x2: float, y2: float, z2: float,
                 x3: float, y3: float, z3: float,
                 x4: float, y4: float, z4: float,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 filled: bool = False, always_on_top: bool = True) -> int:
        key = ((x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4))
        if key in self.rects_idx:
            del self.rects[self.rects_idx[key]]
            del self.rects_idx[key]
        eid = _new_id()
        self.rects[eid] = (x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, r, g, b, a, filled, always_on_top)
        self.rects_idx[key] = eid
        if len(self.rects) > self.max_size:
            self._evict(self.rects, self.rects_idx,
                        lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5]), (e[6], e[7], e[8]), (e[9], e[10], e[11])))
        return eid

    def remove_rect(self,
                    x1: float = None, y1: float = None, z1: float = None,
                    x2: float = None, y2: float = None, z2: float = None,
                    x3: float = None, y3: float = None, z3: float = None,
                    x4: float = None, y4: float = None, z4: float = None,
                    id: int = None) -> None:
        if id is not None:
            self._remove_by_id(self.rects, self.rects_idx,
                                lambda e: ((e[0], e[1], e[2]), (e[3], e[4], e[5]), (e[6], e[7], e[8]), (e[9], e[10], e[11])),
                                id)
        else:
            self._remove_by_key(self.rects, self.rects_idx,
                                 ((x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4)))

    def get_rect_list(self) -> dict:
        return self.rects

    # ── Visibility / toggle ───────────────────────────────────────────────────

    def show_wr(self, enable: bool) -> None:
        global show
        show = enable

    def use_toggle_key(self, enable: bool) -> None:
        global _toggle_listener
        if enable and _toggle_listener is None:
            _toggle_listener = add_event_listener("key", _on_press_key)
        elif not enable and _toggle_listener is not None:
            remove_event_listener(_toggle_listener)
            _toggle_listener = None

    def set_toggle_key(self, tk: int) -> None:
        global toggle_key
        toggle_key = tk

_wr = WorldRender()

def _render_boxes() -> None:
    boxes = _wr.get_box_list()
    if not boxes:
        return

    for entry in boxes.values():
        x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        gizmo = Gizmos.cuboid(AABB(x1, y1, z1, x2, y2, z2), GizmoStyle.stroke(color))
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_blocks() -> None:
    blocks = _wr.get_block_list()
    if not blocks:
        return

    for entry in blocks.values():
        x, y, z, r, g, b, a, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        gizmo = Gizmos.cuboid(BlockPos(x, y, z), GizmoStyle.stroke(color))
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_texts() -> None:
    texts = _wr.get_text_list()
    if not texts:
        return

    for entry in texts.values():
        x, y, z, text, r, g, b, a, size, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        style = TextGizmo_Style.forColorAndCentered(color).withScale(size)
        gizmo = Gizmos.billboardText(text, Vec3(JavaFloat(x), JavaFloat(y), JavaFloat(z)), style)
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_points() -> None:
    points = _wr.get_point_list()
    if not points:
        return

    for entry in points.values():
        x, y, z, r, g, b, a, size, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        gizmo = Gizmos.point(Vec3(JavaFloat(x), JavaFloat(y), JavaFloat(z)), color, JavaFloat(size))
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_lines() -> None:
    lines = _wr.get_line_list()
    if not lines:
        return

    for entry in lines.values():
        x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        start = Vec3(JavaFloat(x1), JavaFloat(y1), JavaFloat(z1))
        end   = Vec3(JavaFloat(x2), JavaFloat(y2), JavaFloat(z2))
        gizmo = Gizmos.line(start, end, color, JavaFloat(width))
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_arrows() -> None:
    arrows = _wr.get_arrow_list()
    if not arrows:
        return

    for entry in arrows.values():
        x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        start = Vec3(JavaFloat(x1), JavaFloat(y1), JavaFloat(z1))
        end   = Vec3(JavaFloat(x2), JavaFloat(y2), JavaFloat(z2))
        gizmo = Gizmos.arrow(start, end, color, JavaFloat(width))
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_circles() -> None:
    circles = _wr.get_circle_list()
    if not circles:
        return

    for entry in circles.values():
        x, y, z, radius, r, g, b, a, filled, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        style = GizmoStyle.fill(color) if filled else GizmoStyle.stroke(color)
        gizmo = Gizmos.circle(Vec3(JavaFloat(x), JavaFloat(y), JavaFloat(z)), JavaFloat(radius), style)
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _render_rects() -> None:
    rects = _wr.get_rect_list()
    if not rects:
        return

    for entry in rects.values():
        x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, r, g, b, a, filled, always_on_top = entry
        color = ARGB.color(a, r, g, b)
        style = GizmoStyle.fill(color) if filled else GizmoStyle.stroke(color)
        a_pos = Vec3(JavaFloat(x1), JavaFloat(y1), JavaFloat(z1))
        b_pos = Vec3(JavaFloat(x2), JavaFloat(y2), JavaFloat(z2))
        c_pos = Vec3(JavaFloat(x3), JavaFloat(y3), JavaFloat(z3))
        d_pos = Vec3(JavaFloat(x4), JavaFloat(y4), JavaFloat(z4))
        gizmo = Gizmos.rect(a_pos, b_pos, c_pos, d_pos, style)
        if always_on_top:
            gizmo.setAlwaysOnTop()

def _on_press_key(event) -> None:
    global show

    if event.action == 0 and event.key == toggle_key:
        show = not show

def _on_render(event) -> None:
    if not show:
        return

    _render_texts()
    _render_boxes()
    _render_blocks()
    _render_points()
    _render_lines()
    _render_arrows()
    _render_circles()
    _render_rects()


add_event_listener("render", _on_render)

""")

_wr = pyj_wr.get("_wr")

type BlockPos = tuple[int, int, int]
type Vec3 = tuple[float, float, float]

class WorldRender:

    # ── Boxes ─────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_box(
        x1: int, y1: int, z1: int, x2: int, y2: int, z2: int,
        r: int = 255, g: int = 255, b: int = 255, a: int = 255, /, *,
        always_on_top: bool = True
    ) -> int:
        ...

    @overload
    @staticmethod
    def add_box(
        pos1: BlockPos, pos2: BlockPos,
        rgba: tuple[int, int, int, int], /, *,
        always_on_top: bool = True
    ) -> int:
        ...
        
    @staticmethod
    def add_box(
        x1: int | BlockPos,
        y1: int | BlockPos,
        z1: int | tuple[int, int, int, int] | None = None,
        x2: int | None = None,
        y2: int | None = None,
        z2: int | None = None,
        r: int = 255,
        g: int = 255,
        b: int = 255,
        a: int = 255, /, *,
        always_on_top: bool = True
    ) -> int:
        """
        Add a box at the specified integer world coordinates.

        This function supports two overloads:

        1. Individual coordinates: add_box(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, always_on_top=True)

        2. Position tuples: add_box(pos1, pos2, rgba, always_on_top=True)

        Args:
            For the first overload:
                x1 (int): X coordinate of position1 (integer grid position).
                y1 (int): Y coordinate of position1 (integer grid position).
                z1 (int): Z coordinate of position1 (integer grid position).
                x2 (int): X coordinate of position2 (integer grid position).
                y2 (int): Y coordinate of position2 (integer grid position).
                z2 (int): Z coordinate of position2 (integer grid position).
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos1 (BlockPos): Tuple of (x1, y1, z1) for position1.
                pos2 (BlockPos): Tuple of (x2, y2, z2) for position2.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this box.
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple) and isinstance(z1, tuple):
            return _wr.add_box(*x1, *y1, *z1, always_on_top) # type: ignore
        else:
            return _wr.add_box(x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top) # type: ignore

    @overload
    @staticmethod
    def remove_box(x1: int=None, y1: int=None, z1: int=None,
                   x2: int=None, y2: int=None, z2: int=None, *,
                   id: int=None) -> None:
        ...

    @overload
    @staticmethod
    def remove_box(pos1: BlockPos, pos2: BlockPos, /, *, id: int=None) -> None:
        ...

    @staticmethod
    def remove_box(x1: int | BlockPos | None=None, y1: int | BlockPos | None=None, z1: int | None = None,
                   x2: int | None = None, y2: int | None = None, z2: int | None = None, *,
                   id: int | None = None) -> None:
        """
        Remove a box by coordinates or by ID.

        Args:
            x1 (int, optional): X coordinate of position1.
            y1 (int, optional): Y coordinate of position1.
            z1 (int, optional): Z coordinate of position1.
            x2 (int, optional): X coordinate of position2.
            y2 (int, optional): Y coordinate of position2.
            z2 (int, optional): Z coordinate of position2.
            id (int, optional): Unique ID returned by add_box. If provided, coordinates are ignored.

        Returns:
            None
        """
        _wr.remove_box(x1, y1, z1, x2, y2, z2, id)

    @staticmethod
    def get_box_list() -> dict:
        """
        Returns the internal mapping of boxes currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x1, y1, z1, x2, y2, z2, r, g, b, a, always_on_top) tuples.
        """
        return _wr.get_box_list() # type: ignore

# ── Blocks ─────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_block(x: int, y: int, z: int, r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                  always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_block(pos: BlockPos, rgba: tuple[int, int, int, int], always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_block(x: int | BlockPos, y: int | tuple[int, int, int, int] | None = None, z: int | None = None,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255, always_on_top: bool = True) -> int:
        """
        Add a block at the specified integer world coordinates.

        This function supports two overloads:

        1. Individual coordinates: add_block(x, y, z, r=255, g=255, b=255, a=255, always_on_top=True)

        2. Position tuple: add_block(pos, rgba, always_on_top=True)

        Args:
            For the first overload:
                x (int): X coordinate of the block (integer grid position).
                y (int): Y coordinate of the block (integer grid position).
                z (int): Z coordinate of the block (integer grid position).
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos (BlockPos): Tuple of (x, y, z) for the block position.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this block.
        """
        if isinstance(x, tuple) and isinstance(y, tuple):
            return _wr.add_block(*x, *y, always_on_top)  # type: ignore
        else:
            return _wr.add_block(x, y, z, r, g, b, a, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_block(x: int = None, y: int = None, z: int = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_block(pos: BlockPos, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_block(x: int | BlockPos | None = None,
                     y: int | None = None,
                     z: int | None = None, *,
                     id: int | None = None) -> None:
        """
        Remove a block by coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_block(x, y, z, id=None)

        2. Position tuple: remove_block(pos, id=None)

        Args:
            For the first overload:
                x (int, optional): X coordinate of the block.
                y (int, optional): Y coordinate of the block.
                z (int, optional): Z coordinate of the block.
                id (int, optional): Unique ID returned by add_block. If provided, coordinates are ignored.

            For the second overload:
                pos (BlockPos): Tuple of (x, y, z) for the block position.
                id (int, optional): Unique ID returned by add_block. If provided, position is ignored.

        Returns:
            None
        """
        if isinstance(x, tuple):
            _wr.remove_block(*x, id)
        else:
            _wr.remove_block(x, y, z, id)

    @staticmethod
    def get_block_list() -> dict:
        """
        Returns the internal mapping of blocks currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x, y, z, r, g, b, a, always_on_top) tuples.
        """
        return _wr.get_block_list() # type: ignore

    # ── Texts ─────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_text(x: float, y: float, z: float,
                 text: str,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 size: float = 1.0, /, *,
                 always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_text(pos: Vec3,
                 text: str,
                 rgba: tuple[int, int, int, int],
                 size: float = 1.0, /, *,
                 always_on_top: bool = True) -> int:
        ...

    @staticmethod
    def add_text(x: float | Vec3,
                 y: float | str | None = None,
                 z: float | tuple[int, int, int, int] | None = None,
                 text: str | float = "",
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 size: float = 1.0, /, *, always_on_top: bool = True) -> int:
        """
        Add a floating text label at the specified world coordinates.

        This function supports two overloads:

        1. Individual coordinates: add_text(x, y, z, text, r=255, g=255, b=255, a=255, size=1.0, always_on_top=True)

        2. Position tuple: add_text(pos, text, rgba, size=1.0, always_on_top=True)

        Args:
            For the first overload:
                x (float): X coordinate in world space.
                y (float): Y coordinate in world space.
                z (float): Z coordinate in world space.
                text (str): The text to render.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                size (float, optional): Scale/size multiplier for the rendered text. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the text position.
                text (str): The text to render.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                size (float, optional): Scale/size multiplier for the rendered text. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this text.
        """
        if isinstance(x, tuple) and isinstance(y, str) and isinstance(z, tuple):
            return _wr.add_text(*x, y, *z, size, always_on_top)  # type: ignore
        else:
            return _wr.add_text(x, y, z, text, r, g, b, a, size, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_text(x: float = None, y: float = None, z: float = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_text(pos: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_text(x: float | Vec3 | None = None,
                    y: float | None = None,
                    z: float | None = None, *,
                    id: int | None = None) -> None:
        """
        Remove a floating text label by coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_text(x, y, z, id=None)

        2. Position tuple: remove_text(pos, id=None)

        Args:
            For the first overload:
                x (float, optional): X coordinate in world space.
                y (float, optional): Y coordinate in world space.
                z (float, optional): Z coordinate in world space.
                id (int, optional): Unique ID returned by add_text. If provided, coordinates are ignored.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the text position.
                id (int, optional): Unique ID returned by add_text. If provided, position is ignored.

        Returns:
            None
        """
        if isinstance(x, tuple):
            _wr.remove_text(*x, id)
        else:
            _wr.remove_text(x, y, z, id)

    @staticmethod
    def get_text_list() -> dict:
        """
        Returns the internal mapping of floating texts currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x, y, z, text, r, g, b, a, size, always_on_top) tuples.
        """
        return _wr.get_text_list() # type: ignore

    # ── Points ────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_point(x: float, y: float, z: float, r: int = 255, g: int = 255, b: int = 255,
                  a: int = 255, size: float = 4.0, always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_point(pos: Vec3, rgba: tuple[int, int, int, int], size: float = 4.0,
                  always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_point(x: float | Vec3, y: float | tuple[int, int, int, int] | None = None, z: float | None = None,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255, size: float = 4.0,
                  always_on_top: bool = True) -> int:
        """
        Add a point at the specified world coordinates.

        This function supports two overloads:

        1. Individual coordinates: add_point(x, y, z, r=255, g=255, b=255, a=255, size=4.0, always_on_top=True)

        2. Position tuple: add_point(pos, rgba, size=4.0, always_on_top=True)

        Args:
            For the first overload:
                x (float): X coordinate in world space.
                y (float): Y coordinate in world space.
                z (float): Z coordinate in world space.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                size (float, optional): Rendered size of the point. Defaults to 4.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the point position.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                size (float, optional): Rendered size of the point. Defaults to 4.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this point.
        """
        if isinstance(x, tuple) and isinstance(y, tuple):
            return _wr.add_point(*x, *y, size, always_on_top)  # type: ignore
        else:
            return _wr.add_point(x, y, z, r, g, b, a, size, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_point(x: float = None, y: float = None, z: float = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_point(pos: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_point(x: float | Vec3 | None = None,
                    y: float | None = None,
                    z: float | None = None, *,
                    id: int | None = None) -> None:
        """
        Remove a point by coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_point(x, y, z, id=None)

        2. Position tuple: remove_point(pos, id=None)

        Args:
            For the first overload:
                x (float, optional): X coordinate in world space.
                y (float, optional): Y coordinate in world space.
                z (float, optional): Z coordinate in world space.
                id (int, optional): Unique ID returned by add_point. If provided, coordinates are ignored.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the point position.
                id (int, optional): Unique ID returned by add_point. If provided, position is ignored.

        Returns:
            None
        """
        if isinstance(x, tuple):
            _wr.remove_point(*x, id)
        else:
            _wr.remove_point(x, y, z, id)

    @staticmethod
    def get_point_list() -> dict:
        """
        Returns the internal mapping of points currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x, y, z, r, g, b, a, size, always_on_top) tuples.
        """
        return _wr.get_point_list() # type: ignore

    # ── Lines ─────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_line(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255, width: float = 1.0,
                 always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_line(pos1: Vec3, pos2: Vec3, rgba: tuple[int, int, int, int], width: float = 1.0,
                 always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_line(x1: float | Vec3, y1: float | Vec3 | None = None, z1: float | tuple[int, int, int, int] | None = None,
                 x2: float | None = None, y2: float | None = None, z2: float | None = None,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255, width: float = 1.0,
                 always_on_top: bool = True) -> int:
        """
        Add a line segment between two world-space points.

        This function supports two overloads:

        1. Individual coordinates: add_line(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, width=1.0, always_on_top=True)

        2. Position tuples: add_line(pos1, pos2, rgba, width=1.0, always_on_top=True)

        Args:
            For the first overload:
                x1 (float): X coordinate of the start point.
                y1 (float): Y coordinate of the start point.
                z1 (float): Z coordinate of the start point.
                x2 (float): X coordinate of the end point.
                y2 (float): Y coordinate of the end point.
                z2 (float): Z coordinate of the end point.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                width (float, optional): Line width. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the start point.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the end point.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                width (float, optional): Line width. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this line.
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple) and isinstance(z1, tuple):
            return _wr.add_line(*x1, *y1, *z1, width, always_on_top)  # type: ignore
        else:
            return _wr.add_line(x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_line(x1: float = None, y1: float = None, z1: float = None, x2: float = None,
                    y2: float = None, z2: float = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_line(pos1: Vec3, pos2: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_line(x1: float | Vec3 | None = None, y1: float | Vec3 | None = None, z1: float | None = None,
                    x2: float | None = None, y2: float | None = None, z2: float | None = None, *, id: int | None = None) -> None:
        """
        Remove a line segment by endpoint coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_line(x1, y1, z1, x2, y2, z2, id=None)

        2. Position tuples: remove_line(pos1, pos2, id=None)

        Args:
            For the first overload:
                x1 (float, optional): X coordinate of the start point.
                y1 (float, optional): Y coordinate of the start point.
                z1 (float, optional): Z coordinate of the start point.
                x2 (float, optional): X coordinate of the end point.
                y2 (float, optional): Y coordinate of the end point.
                z2 (float, optional): Z coordinate of the end point.
                id (int, optional): Unique ID returned by add_line. If provided, coordinates are ignored.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the start point.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the end point.
                id (int, optional): Unique ID returned by add_line. If provided, positions are ignored.

        Returns:
            None
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple):
            _wr.remove_line(*x1, *y1, id)
        else:
            _wr.remove_line(x1, y1, z1, x2, y2, z2, id)

    @staticmethod
    def get_line_list() -> dict:
        """
        Returns the internal mapping of lines currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top) tuples.
        """
        return _wr.get_line_list() # type: ignore

    # ── Arrows ────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_arrow(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255, width: float = 1.0,
                  always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_arrow(pos1: Vec3, pos2: Vec3, rgba: tuple[int, int, int, int], width: float = 1.0,
                  always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_arrow(x1: float | Vec3, y1: float | Vec3 | None = None, z1: float | tuple[int, int, int, int] | None = None,
                  x2: float | None = None, y2: float | None = None, z2: float | None = None,
                  r: int = 255, g: int = 255, b: int = 255, a: int = 255, width: float = 1.0,
                  always_on_top: bool = True) -> int:
        """
        Add an arrow from a start point to an end point in world space.

        This function supports two overloads:

        1. Individual coordinates: add_arrow(x1, y1, z1, x2, y2, z2, r=255, g=255, b=255, a=255, width=1.0, always_on_top=True)

        2. Position tuples: add_arrow(pos1, pos2, rgba, width=1.0, always_on_top=True)

        Args:
            For the first overload:
                x1 (float): X coordinate of the arrow tail.
                y1 (float): Y coordinate of the arrow tail.
                z1 (float): Z coordinate of the arrow tail.
                x2 (float): X coordinate of the arrow head.
                y2 (float): Y coordinate of the arrow head.
                z2 (float): Z coordinate of the arrow head.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                width (float, optional): Shaft width. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the arrow tail.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the arrow head.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                width (float, optional): Shaft width. Defaults to 1.0.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this arrow.
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple) and isinstance(z1, tuple):
            return _wr.add_arrow(*x1, *y1, *z1, width, always_on_top)  # type: ignore
        else:
            return _wr.add_arrow(x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_arrow(x1: float = None, y1: float = None, z1: float = None, x2: float = None,
                     y2: float = None, z2: float = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_arrow(pos1: Vec3, pos2: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_arrow(x1: float | Vec3 | None = None, y1: float | Vec3 | None = None, z1: float | None = None,
                     x2: float | None = None, y2: float | None = None, z2: float | None = None, *, id: int | None = None) -> None:
        """
        Remove an arrow by endpoint coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_arrow(x1, y1, z1, x2, y2, z2, id=None)

        2. Position tuples: remove_arrow(pos1, pos2, id=None)

        Args:
            For the first overload:
                x1 (float, optional): X coordinate of the arrow tail.
                y1 (float, optional): Y coordinate of the arrow tail.
                z1 (float, optional): Z coordinate of the arrow tail.
                x2 (float, optional): X coordinate of the arrow head.
                y2 (float, optional): Y coordinate of the arrow head.
                z2 (float, optional): Z coordinate of the arrow head.
                id (int, optional): Unique ID returned by add_arrow. If provided, coordinates are ignored.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the arrow tail.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the arrow head.
                id (int, optional): Unique ID returned by add_arrow. If provided, positions are ignored.

        Returns:
            None
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple):
            _wr.remove_arrow(*x1, *y1, id)
        else:
            _wr.remove_arrow(x1, y1, z1, x2, y2, z2, id)

    @staticmethod
    def get_arrow_list() -> dict:
        """
        Returns the internal mapping of arrows currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x1, y1, z1, x2, y2, z2, r, g, b, a, width, always_on_top) tuples.
        """
        return _wr.get_arrow_list() # type: ignore

    # ── Circles ───────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_circle(x: float, y: float, z: float, radius: float, r: int = 255, g: int = 255,
                   b: int = 255, a: int = 255, filled: bool = False, always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_circle(pos: Vec3, radius: float, rgba: tuple[int, int, int, int], filled: bool = False,
                   always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_circle(x: float | Vec3, y: float | float | None = None, z: float | tuple[int, int, int, int] | None = None,
                   radius: float | None = None, r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                   filled: bool = False, always_on_top: bool = True) -> int:
        """
        Add a circle centered at the specified world coordinates.

        This function supports two overloads:

        1. Individual coordinates: add_circle(x, y, z, radius, r=255, g=255, b=255, a=255, filled=False, always_on_top=True)

        2. Position tuple: add_circle(pos, radius, rgba, filled=False, always_on_top=True)

        Args:
            For the first overload:
                x (float): X coordinate of the center in world space.
                y (float): Y coordinate of the center in world space.
                z (float): Z coordinate of the center in world space.
                radius (float): Radius of the circle in world units.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                filled (bool, optional): If True, renders a filled disc; otherwise renders an outline. Defaults to False.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the center position.
                radius (float): Radius of the circle in world units.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                filled (bool, optional): If True, renders a filled disc; otherwise renders an outline. Defaults to False.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this circle.
        """
        if isinstance(x, tuple) and isinstance(y, (int, float)) and isinstance(z, tuple):
            return _wr.add_circle(*x, y, *z, filled, always_on_top)  # type: ignore
        else:
            return _wr.add_circle(x, y, z, radius, r, g, b, a, filled, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_circle(x: float = None, y: float = None, z: float = None, *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_circle(pos: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_circle(x: float | Vec3 | None = None, y: float | None = None, z: float | None = None, *, id: int | None = None) -> None:
        """
        Remove a circle by its center coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_circle(x, y, z, id=None)

        2. Position tuple: remove_circle(pos, id=None)

        Args:
            For the first overload:
                x (float, optional): X coordinate of the center in world space.
                y (float, optional): Y coordinate of the center in world space.
                z (float, optional): Z coordinate of the center in world space.
                id (int, optional): Unique ID returned by add_circle. If provided, coordinates are ignored.

            For the second overload:
                pos (Vec3): Tuple of (x, y, z) for the center position.
                id (int, optional): Unique ID returned by add_circle. If provided, position is ignored.

        Returns:
            None
        """
        if isinstance(x, tuple):
            _wr.remove_circle(*x, id)
        else:
            _wr.remove_circle(x, y, z, id)

    @staticmethod
    def get_circle_list() -> dict:
        """
        Returns the internal mapping of circles currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are (x, y, z, radius, r, g, b, a, filled, always_on_top) tuples.
        """
        return _wr.get_circle_list() # type: ignore

    # ── Rects ─────────────────────────────────────────────────────────────────

    @overload
    @staticmethod
    def add_rect(x1: float, y1: float, z1: float,
                 x2: float, y2: float, z2: float,
                 x3: float, y3: float, z3: float,
                 x4: float, y4: float, z4: float,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 filled: bool = False, always_on_top: bool = True) -> int:
        ...

    @overload
    @staticmethod
    def add_rect(pos1: Vec3, pos2: Vec3, pos3: Vec3, pos4: Vec3,
                 rgba: tuple[int, int, int, int], filled: bool = False, always_on_top: bool = True, /) -> int:
        ...

    @staticmethod
    def add_rect(x1: float | Vec3, y1: float | Vec3 | None = None, z1: float | Vec3 | None = None,
                 x2: float | Vec3 | None = None, y2: float | tuple[int, int, int, int] | None = None, z2: float | None = None,
                 x3: float | None = None, y3: float | None = None, z3: float | None = None,
                 x4: float | None = None, y4: float | None = None, z4: float | None = None,
                 r: int = 255, g: int = 255, b: int = 255, a: int = 255,
                 filled: bool = False, always_on_top: bool = True) -> int:
        """
        Add a quadrilateral defined by four world-space corner vertices.

        Vertices should be specified in order (e.g. clockwise or counter-clockwise)
        to form a valid planar quad.

        This function supports two overloads:

        1. Individual coordinates: add_rect(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, r=255, g=255, b=255, a=255, filled=False, always_on_top=True)

        2. Position tuples: add_rect(pos1, pos2, pos3, pos4, rgba, filled=False, always_on_top=True)

        Args:
            For the first overload:
                x1, y1, z1 (float): First corner position.
                x2, y2, z2 (float): Second corner position.
                x3, y3, z3 (float): Third corner position.
                x4, y4, z4 (float): Fourth corner position.
                r (int, optional): Red channel value in the range 0–255. Defaults to 255.
                g (int, optional): Green channel value in the range 0–255. Defaults to 255.
                b (int, optional): Blue channel value in the range 0–255. Defaults to 255.
                a (int, optional): Alpha/opacity channel in the range 0–255. Defaults to 255 (opaque).
                filled (bool, optional): If True, renders a filled quad; otherwise renders an outline. Defaults to False.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the first corner.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the second corner.
                pos3 (Vec3): Tuple of (x3, y3, z3) for the third corner.
                pos4 (Vec3): Tuple of (x4, y4, z4) for the fourth corner.
                rgba (tuple[int, int, int, int]): Tuple of (r, g, b, a) color values.
                filled (bool, optional): If True, renders a filled quad; otherwise renders an outline. Defaults to False.
                always_on_top (bool, optional): If True, renders through blocks. Defaults to True.

        Returns:
            int: Unique ID assigned to this rect.
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple) and isinstance(z1, tuple) and isinstance(x2, tuple) and isinstance(y2, tuple):
            return _wr.add_rect(*x1, *y1, *z1, *x2, *y2, z2, x3)  # type: ignore
        else:
            return _wr.add_rect(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, r, g, b, a, filled, always_on_top)  # type: ignore

    @overload
    @staticmethod
    def remove_rect(x1: float = None, y1: float = None, z1: float = None,
                    x2: float = None, y2: float = None, z2: float = None,
                    x3: float = None, y3: float = None, z3: float = None,
                    x4: float = None, y4: float = None, z4: float = None,
                    *, id: int = None) -> None:
        ...

    @overload
    @staticmethod
    def remove_rect(pos1: Vec3, pos2: Vec3, pos3: Vec3, pos4: Vec3, /, *, id: int = None) -> None:
        ...

    @staticmethod
    def remove_rect(x1: float | Vec3 | None = None,
                    y1: float | Vec3 | None = None,
                    z1: float | Vec3 | None = None,
                    x2: float | Vec3 | None = None,
                    y2: float | None = None,
                    z2: float | None = None,
                    x3: float | None = None,
                    y3: float | None = None,
                    z3: float | None = None,
                    x4: float | None = None,
                    y4: float | None = None,
                    z4: float | None = None, *,
                    id: int | None = None) -> None:
        """
        Remove a quadrilateral by its four corner coordinates or by ID.

        This function supports two overloads:

        1. Individual coordinates: remove_rect(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, id=None)

        2. Position tuples: remove_rect(pos1, pos2, pos3, pos4, id=None)

        Args:
            For the first overload:
                x1, y1, z1 (float, optional): First corner position.
                x2, y2, z2 (float, optional): Second corner position.
                x3, y3, z3 (float, optional): Third corner position.
                x4, y4, z4 (float, optional): Fourth corner position.
                id (int, optional): Unique ID returned by add_rect. If provided, coordinates are ignored.

            For the second overload:
                pos1 (Vec3): Tuple of (x1, y1, z1) for the first corner.
                pos2 (Vec3): Tuple of (x2, y2, z2) for the second corner.
                pos3 (Vec3): Tuple of (x3, y3, z3) for the third corner.
                pos4 (Vec3): Tuple of (x4, y4, z4) for the fourth corner.
                id (int, optional): Unique ID returned by add_rect. If provided, positions are ignored.

        Returns:
            None
        """
        if isinstance(x1, tuple) and isinstance(y1, tuple) and isinstance(z1, tuple) and isinstance(x2, tuple):
            _wr.remove_rect(*x1, *y1, *z1, *x2, id)
        else:
            _wr.remove_rect(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, id)

    @staticmethod
    def get_rect_list() -> dict:
        """
        Returns the internal mapping of quads currently tracked by the WorldRender.

        Returns:
            dict: Mapping where keys are int IDs and values are
                  (x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4, r, g, b, a, filled, always_on_top) tuples.
        """
        return _wr.get_rect_list() # type: ignore

    # ── Visibility / toggle ───────────────────────────────────────────────────

    @staticmethod
    def show_wr(enable: bool):
        """
        Enables or disables display of all wr content.

        Args:
            enable (bool): True to show, False to hide.
        """
        _wr.show_wr(enable)

    @staticmethod
    def use_toggle_key(enable: bool):
        """
        Enables or disables the wr toggle key (default F12).

        Args:
            enable (bool): True to allow toggling wr with key.
        """
        _wr.use_toggle_key(enable)

    @staticmethod
    def set_toggle_key(toggle_key: int):
        """
        Sets the key code used to toggle wr display (GLFW key code).

        Args:
            toggle_key (int): GLFW key code to use for toggling.
        """
        _wr.set_toggle_key(toggle_key)
